"""
Address-related aggregate tools.
"""
import functools

from src.core.connector import fetch_address_data, fetch_address_balances
from src.core.db import unwrap_into_table, setup_sqlite_connection, get_aggregate
from src.core.enums import AddressDataSource
from src.core.utils import collect_all_pages
from .aggregate_schemas import get_balance_schema_description
from .registry import mcp_tool


@mcp_tool
async def aggregate_address_mempool(blockchain: str, module: str, address: str, sql_query: str):
    """
    Aggregate *pending mempool transfers* for an address in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - transaction_hash: transaction hash as text
        - time: ISO timestamp of the mempool event as text
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - currency_decimals: number of decimals for the currency. 0 if the currency is indivisible(nft).
        - currency_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        - effect: amount in the smallest units as REAL type. Positive if the address is receiver, negative if is sender.
        - failed: boolean indicating whether transaction failed or null if not applicable
        - extra: Special marker describing the type of transfer as text field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
    Args:
        blockchain (str): blockchain to fetch from
        module (str): module of the blockchain.
            Must always be prepended with blockchain name. Example: "arbitrum-one-erc-20".
        address (str): address to get mempool data for
        sql_query (str): sqlite syntax query to aggregate transfer data
    Returns:
        dict: aggregated result of a query
    """
    conn = setup_sqlite_connection()
    # validate_sql(conn, sql_query)

    all_mempool_events = await collect_all_pages(
        functools.partial(fetch_address_data, blockchain=blockchain, module=module, address=address,
                          source=AddressDataSource.mempool),
        data_keys=["data", "mempool", module], get_currency_info=True, stop_after_first=False,
    )
    
    mempool_schema = {
        "transaction_hash": "TEXT", 
        "time": "TEXT", 
        "currency_id": "TEXT",
        "currency_symbol": "TEXT",
        "currency_decimals": "TINYINT",
        "currency_verified": "BOOLEAN", 
        "exchange_rate": "REAL",
        "effect": "REAL", 
        "failed": "BOOLEAN", 
        "extra": "TEXT"
    }
    
    unwrap_into_table(conn, mempool_schema, all_mempool_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


@mcp_tool
async def aggregate_address_balances(blockchain: str, module: str, address: str, sql_query: str):
    f"""
    Aggregate *balance info* for an address in requested blockchain within requested module in a sqlite table.
    {get_balance_schema_description()}
    Additional details:
        - In case if you query main module, there will be only one row (example with `ethereum-main`):
          currency_id: "ethereum", symbol: "ETH", decimals: 18, balance: "237558121960475169592"
        - When you query other modules, the currency will be in form of an address prepended with module name:
          currency_id: "ethereum-erc-20/0xdAC...1ec7", symbol: "USDT", decimals: 18, balance: "113231423123"

    Args:
        blockchain (str): Blockchain to fetch from.
        module (str): Module of the blockchain.
            Must always be prepended with blockchain name. Example: "arbitrum-one-erc-20".
        address (str): Address to get balances for.
        sql_query (str): SQLite syntax query to aggregate balance data.
    Returns:
        dict: aggregated result of a query
    """
    conn = setup_sqlite_connection()
    # validate_sql(conn, sql_query)

    all_balances = await collect_all_pages(
        functools.partial(fetch_address_balances, blockchain=blockchain, module=module, address=address,
                          source=AddressDataSource.balances),
        [], get_currency_info=False, stop_after_first=module.endswith("-main")
    )
    
    balance_schema = {
        "currency_id": "TEXT", 
        "symbol": "TEXT", 
        "decimals": "INT", 
        "balance": "REAL", 
        "is_verified": "BOOLEAN",
        "exchange_rate": "REAL"
    }
    
    unwrap_into_table(conn, balance_schema, all_balances)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


@mcp_tool
async def aggregate_address_transfers(blockchain: str, module: str, address: str, sql_query: str):
    """
    Aggregate *confirmed individual transfers* for an address in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - block: block height as integer
        - transaction_hash: transaction hash as text
        - time: ISO timestamp of the event as text
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - currency_decimals: number of decimals for the currency. 0 if the currency is indivisible(nft).
        - currency_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - effect: amount in the smallest units as REAL type. Positive if the address is receiver, negative if is sender.
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        - failed: boolean indicating whether transaction failed
        - extra: Special marker describing the type of transfer as text field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
    Args:
        blockchain (str): blockchain to fetch from
        module (str): module of the blockchain
            Must always be prepended with blockchain name. Example: "arbitrum-one-erc-20".
        address (str): address to get transfer data for
        sql_query (str): sqlite syntax query to aggregate transfer data
    Returns:
        dict: aggregated result of a query
    """
    conn = setup_sqlite_connection()
    # validate_sql(conn, sql_query)

    all_address_events = await collect_all_pages(
        functools.partial(fetch_address_data, blockchain=blockchain, module=module, address=address,
                          source=AddressDataSource.events),
        data_keys=["data", "events", module], get_currency_info=True, stop_after_first=False
    )
    
    address_transfer_schema = {
        "block": "INT", 
        "transaction_hash": "TEXT", 
        "time": "TEXT", 
        "currency_id": "TEXT",
        "currency_symbol": "TEXT",
        "currency_decimals": "TINYINT",
        "currency_verified": "BOOLEAN", 
        "exchange_rate": "REAL",
        "effect": "REAL", 
        "failed": "BOOLEAN", 
        "extra": "TEXT"
    }
    
    unwrap_into_table(conn, address_transfer_schema, all_address_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate