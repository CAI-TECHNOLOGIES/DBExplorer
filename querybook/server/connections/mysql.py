from typing import Optional

from .local_typing import ACLControl, MetastoreData, QueryEngineData


def _convert_mysql_connection_uri(connection_uri: str) -> str:
    """Convert to appropriate mysql connection string for sqlalchemy"""

    if connection_uri.startswith("mysql://"):
        return "".join(["mysql+pymysql://"] + connection_uri.split("://")[1:])

    return connection_uri


def mysql_connection_query_executor_mapper(
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
            "connection_string": _convert_mysql_connection_uri(connection_uri),
            "connect_args": [],
        },
        "language": "mysql",
        "feature_param": {
            "status_checker": "ConnectionChecker",
            "upload_exporter": "SqlalchemyExporter",
        },
        "metastore_id": metastore_id,
    }


def mysql_connection_metastore_mapper(
    name: str,
    connection_uri: str,
    extra_params: dict,
    acl_control: Optional[ACLControl] = None,
) -> MetastoreData:
    # TODO convert extra_params to connect_args, other fields
    return {
        "name": name,
        "acl_control": acl_control,
        "loader": "SqlAlchemyMetastoreLoader",
        "metastore_params": {
            "connection_string": _convert_mysql_connection_uri(connection_uri),
            "connect_args": [],
        },
    }
