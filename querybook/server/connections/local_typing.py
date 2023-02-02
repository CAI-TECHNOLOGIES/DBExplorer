from typing import Callable, Dict, Optional, TypedDict, Literal


class ACLControl(TypedDict):
    type: str
    tables: list[str]


MetadataLoaderLiteral = Literal[
    "SqlAlchemyMetastoreLoader",
    "HMSMetastoreLoader",
    "HMSThriftMetastoreLoader",
    "GlueDataCatalogLoader",
    "MysqlMetastoreLoader",
]

QueryEngineLiteral = Literal["postgresql", "mysql", "elasticsearch"]


class MetastoreData(TypedDict):
    name: str
    acl_control: Optional[ACLControl]
    loader: MetadataLoaderLiteral
    metastore_params: Dict


class ExecutorParams(TypedDict):
    connect_args: list
    connection_string: str


class QueryEngineData(TypedDict):
    # name:
    name: str
    description: Optional[str]
    langauge: QueryEngineLiteral
    executor: str  # TODO: map it to the allowed literal types.
    executor_params: ExecutorParams
    feature_param: Dict
    metastore_id: Optional[str]


class ConnectionMetastoreMapper(TypedDict):
    metastore_fn: Callable[(...), MetastoreData]
    query_engine_fn: Callable[(...), QueryEngineData]
