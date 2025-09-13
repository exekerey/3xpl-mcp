"""
Block-related aggregate tools.
"""
import functools

from src.core.connector import fetch_block_events
from src.core.db import setup_sqlite_connection
from src.core.utils import collect_all_pages
from .aggregate_schemas import TRANSFERS_SCHEMA, get_transfer_schema_description
from .registry import mcp_tool
from .validation import (
    validate_blockchain_name, validate_module_name, 
    validate_block_height, safe_execute_sql
)


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
    # Validate inputs
    validate_blockchain_name(blockchain)
    validate_module_name(module, blockchain)
    validate_block_height(height)
    
    conn = setup_sqlite_connection()

    all_block_events = await collect_all_pages(
        functools.partial(fetch_block_events, blockchain=blockchain, module=module, height=height),
        ["data", "events", module], get_currency_info=True, stop_after_first=False,
    )
    
    return safe_execute_sql(conn, TRANSFERS_SCHEMA, all_block_events, sql_query)