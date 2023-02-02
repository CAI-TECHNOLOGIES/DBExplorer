from typing import Dict, List, Optional, Set, TypedDict

from sqlalchemy.orm import Session

from app.db import with_session
from app.flask_app import celery
from models.admin import QueryEngine, QueryMetastore
from models.environment import Environment, UserEnvironment
from models.user import User
from connections import c_meta_map
from logic.admin import add_query_engine_to_environment


class UserDict(TypedDict):
    """User Dict structure"""

    fullname: str
    email: str
    id: int


class ConnectionDict(TypedDict):
    """Connection Dict structure"""

    name: str
    description: Optional[str]
    type: str
    uri: str


ConnectionsDict = Dict[str, ConnectionDict]


class ProjectConnectionsDict(TypedDict):
    name: str
    description: Optional[str]
    connections: ConnectionsDict


class ProjectDict(TypedDict):
    """Project Dict structure"""

    name: str
    description: Optional[str]
    users: List[str]


class UserProjectMetadata(TypedDict):
    """User Project Dict structure"""

    users: Dict[str, UserDict]
    projects: Dict[int, ProjectDict]


@with_session
def lazy_sync_environments(projects_data: Dict[int, ProjectDict], session: Session):
    """Add new Projects to Environments"""

    project_id_set = set(projects_data)
    existing_envs: List[Environment] = (
        session.query(Environment).filter(Environment.id.in_(project_id_set)).all()
    )
    existing_env_id_set: Set[int] = {env.id for env in existing_envs}
    new_projects_set = project_id_set - existing_env_id_set
    stale_env_id_set = existing_env_id_set - project_id_set

    session.query(Environment).filter(Environment.id.in_(stale_env_id_set)).delete(
        synchronize_session=False
    )

    for env_id in new_projects_set:
        env = Environment(
            id=env_id,
            name=projects_data[env_id]["name"],
            description=projects_data[env_id]["description"],
            public=False,
            hidden=True,
            shareable=True,
        )
        session.add(env)
    session.commit()


@with_session
def lazy_sync_users(user_data: Dict[str, UserDict], session: Session):
    username_set = set(user_data)
    existing_users: List[User] = (
        session.query(User).filter(User.username.in_(username_set)).all()
    )
    existing_username_set: Set[str] = {user.username for user in existing_users}
    stale_username_set = existing_username_set - username_set
    new_username_set = username_set - existing_username_set

    session.query(User).filter(User.username.in_(stale_username_set)).delete(
        synchronize_session=False
    )

    for user in existing_users:
        if user.username in stale_username_set:
            continue
        user_data[user.username]["id"] = user.id

    new_user_objs: List[User] = []
    for username in new_username_set:
        user = User(
            username=username,
            fullname=user_data[username]["fullname"],
            email=user_data[username]["email"],
        )
        new_user_objs.append(user)
        session.add(user)
    session.commit()

    for user in new_user_objs:
        user_data[user.username]["id"] = user.id


@with_session
def lazy_sync_environment_users(user_data: UserProjectMetadata, session: Session):
    """Sync user project assignments."""

    for project_id in set(user_data["projects"]):
        existing_mappings = set(
            session.query(UserEnvironment.user_id, UserEnvironment.environment_id)
            .filter(UserEnvironment.environment_id == project_id)
            .all()
        )
        data_mappings = {
            (user_data["users"][username]["id"], project_id)
            for username in user_data["projects"][project_id]["users"]
        }
        new_mappings = data_mappings - existing_mappings
        stale_mappings = existing_mappings - data_mappings

        for mapping in new_mappings:
            session.add(UserEnvironment(user_id=mapping[0], environment_id=mapping[1]))
        session.commit()

        for stale_mapping in stale_mappings:
            session.query(UserEnvironment).filter(
                UserEnvironment.user_id == stale_mapping[0],
                UserEnvironment.environment_id == stale_mapping[1],
            ).delete(synchronize_session=False)

        session.commit()


@with_session
def sync_project_connections(
    projects_connections_data: Dict[int, ProjectConnectionsDict],
    session: Session,
):

    for project_id, project in projects_connections_data.items():

        env_name = project["name"]
        for conn_id in project["connections"]:
            conn_type = project["connections"][conn_id]["type"]
            if conn_type not in c_meta_map:
                continue

            connection_name = project["connections"][conn_id]["name"]
            description = project["connections"][conn_id]["description"]
            connection_uri = project["connections"][conn_id]["uri"]

            env_conn_name = f"{env_name}_{connection_name}"

            # create connection's metastore if it does not exist
            if QueryMetastore.get(name=env_conn_name) is not None:
                continue
            # if QueryEngine.get(name=unique_conn_name) is not None:
            #     continue

            c_metastore = c_meta_map[conn_type]["metastore_fn"](
                name=env_conn_name,
                acl_control=None,
                connection_uri=connection_uri,
                extra_params={},
            )
            metastore = QueryMetastore.create(c_metastore, session=session, commit=True)
            c_query_engine = c_meta_map[conn_type]["query_engine_fn"](
                name=env_conn_name,
                connection_uri=connection_uri,
                description=description,
                extra_params={},
                metastore_id=metastore.id,
            )
            query_engine = QueryEngine.create(
                c_query_engine, session=session, commit=True
            )

            add_query_engine_to_environment(
                environment_id=project_id,
                query_engine_id=query_engine.id,
                commit=True,
                session=session,
            )


@celery.task(bind=True)
@with_session
def sync_project_user_environment(
    remote_user_project_data: UserProjectMetadata,
    session: Session,
):

    lazy_sync_environments(remote_user_project_data["projects"], session)
    lazy_sync_users(remote_user_project_data["users"], session)

    lazy_sync_environment_users(remote_user_project_data, session)
