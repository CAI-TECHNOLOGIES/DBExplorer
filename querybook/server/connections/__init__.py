from .elasticsearch import (
    elasticsearch_connection_metastore_mapper,
    elasticsearch_connection_query_executor_mapper,
)
from .local_typing import ConnectionMetastoreMapper
from .mysql import (
    mysql_connection_metastore_mapper,
    mysql_connection_query_executor_mapper,
)
from .postgresql import (
    postgres_connection_metadata_mapper,
    postgres_connection_query_executor_mapper,
)

c_meta_map: dict[str, ConnectionMetastoreMapper] = {
    "postgres": {
        "metastore_fn": postgres_connection_metadata_mapper,
        "query_engine_fn": postgres_connection_query_executor_mapper,
    },
    "mysql": {
        "metastore_fn": mysql_connection_metastore_mapper,
        "query_engine_fn": mysql_connection_query_executor_mapper,
    },
    "elasticsearch": {
        "metastore_fn": elasticsearch_connection_metastore_mapper,
        "query_engine_fn": elasticsearch_connection_query_executor_mapper,
    },
}
