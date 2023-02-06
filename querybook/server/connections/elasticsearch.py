from typing import Optional

from .local_typing import ACLControl, MetastoreData, QueryEngineData


def elasticsearch_connection_metastore_mapper(
    name: str,
    connection_uri: str,
    extra_params: dict,
    acl_control: Optional[ACLControl] = None,
) -> MetastoreData:
    # TODO convert extra_params to connect_args
    return {
        "name": name,
        "acl_control": acl_control,
        "loader": "SqlAlchemyMetastoreLoader",
        "metastore_params": {
            "connection_string": connection_uri,
            "connect_args": [],
        },
    }


def elasticsearch_connection_query_executor_mapper(
    name: str,
    connection_uri: str,
    extra_params: dict,
    description: Optional[str] = None,
    metastore_id: Optional[str] = None,
) -> QueryEngineData:
    # TODO: Extract out items from extra params to connect_args, other fields
    return {
        "name": name,
        "description": description,
        "executor": "sqlalchemy",
        "executor_params": {
            "connection_string": connection_uri,
            "connect_args": [],
        },
        "language": "elasticsearch",
        "feature_param": {
            "status_checker": "ConnectionChecker",
            "upload_exporter": "SqlalchemyExporter",
        },
        "metastore_id": metastore_id,
    }
