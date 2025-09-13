"""
Transaction-related aggregate tools.
"""
import functools

from src.core.connector import fetch_transaction_events
from src.core.db import unwrap_into_table, setup_sqlite_connection, get_aggregate
from src.core.utils import collect_all_pages
from .aggregate_schemas import get_transfer_schema_description
from .registry import mcp_tool


@mcp_tool
async def aggregate_transaction_transfers(blockchain: str, module: str, transaction_hash: str, sql_query: str):
    f"""
    Aggregate *individual transfers* within a transaction in requested blockchain within requested module in a sqlite table.
    {get_transfer_schema_description()}
    Args:
        blockchain (str): blockchain to fetch from
        module (str): module of the blockchain.
            Must always be prepended with blockchain name. Example: "arbitrum-one-erc-20".
        transaction_hash (str): hash of the transaction to aggregate
        sql_query (str): sqlite syntax query to aggregate transfer data
    Returns:
        dict: aggregated result of a query
    """
    conn = setup_sqlite_connection()
    # validate_sql(conn, sql_query)

    all_tx_events = await collect_all_pages(
        functools.partial(fetch_transaction_events, blockchain=blockchain, module=module,
                          transaction_hash=transaction_hash),
        data_keys=["data", "events", module], get_currency_info=True, stop_after_first=False
    )
    
    # Use a schema that matches the transaction data structure
    transaction_schema = {
        "address": "TEXT", 
        "currency_id": "TEXT", 
        "currency_symbol": "TEXT",
        "currency_decimals": "TINYINT",
        "currency_verified": "BOOLEAN", 
        "exchange_rate": "REAL",
        "effect": "REAL", 
        "failed": "BOOLEAN", 
        "extra": "TEXT"
    }
    
    unwrap_into_table(conn, transaction_schema, all_tx_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate