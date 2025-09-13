"""
Block-related aggregate tools.
"""
import functools

from src.core.connector import fetch_block_events
from src.core.db import unwrap_into_table, setup_sqlite_connection, get_aggregate
from src.core.utils import collect_all_pages
from .aggregate_schemas import TRANSFERS_SCHEMA, get_transfer_schema_description
from .registry import mcp_tool


@mcp_tool
async def aggregate_block_transfers(blockchain: str, module: str, height: int, sql_query: str):
    f"""
    Aggregate *individual transfers* within a block in requested blockchain within requested module in a sqlite table.
    {get_transfer_schema_description()}
    Args:
        blockchain (str): blockchain to fetch from
        module (str): module of the blockchain.
            Must always be prepended with blockchain name. Example: "arbitrum-one-erc-20"
        height (int): block height in the requested blockchain
        sql_query (str): sqlite syntax query to aggregate transfer data
    Returns:
        dict: aggregated result of a query
    """
    conn = setup_sqlite_connection()
    # validate_sql(conn, sql_query)

    all_block_events = await collect_all_pages(
        functools.partial(fetch_block_events, blockchain=blockchain, module=module, height=height),
        ["data", "events", module], get_currency_info=True, stop_after_first=False,
    )
    unwrap_into_table(conn, TRANSFERS_SCHEMA, all_block_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate