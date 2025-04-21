import functools
import sys

from src.core.connector import fetch_block_events, fetch_transaction_events, fetch_address_data, \
    fetch_address_balances
from src.core.db import unwrap_into_table, setup_sqlite_connection, get_aggregate
from src.core.enums import AddressDataSource
from src.core.utils import collect_all_pages


# current state of actions:
#  test each tool with Claude, see if it runs, get some edge cases

# TODO: tune tool descriptions better - few issues:
#           - not using is_verified when checking balances
#           - not passing modules correctly unless provided with exact module name(need to make it to look up modules though?)

# todo: "can you give me the biggest in terms of usd transaction of this address?" There is no rates fetched.
# todo: also there is no names for currencies except when querying balances.
# todo: segmenting on an address transfers. For example allowing inputting 30 days range and querying stuff on this range.
#  And then aggregating.
# TODO: extra has more meanings and you gotta paste that somehow into tools.
# TODO: currencies should have is_verified when they are in the data(they are always there)


async def aggregate_block_transfers(blockchain: str, module: str, height: int, sql_query: str):
    """
    Aggregate *individual transfers* within a block in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - transaction_hash: transaction hash as text
        - address: target address of the transfer as text
        - currency: full currency name in lowercase. Prepended with module name and '/' if not-native currency
        - currency_symbol: currency symbol/ticker) in uppercase.
        - effect: amount in the smallest units as REAL type. Positive if gained, negative if spent.
        - failed: boolean indicating whether transaction failed
        - extra: special mark as text. 'f' for miner fee, 'b' for burnt fee, null for regular transfers
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
    unwrap_into_table(
        conn,
        {"transaction_hash": "TEXT", "address": "TEXT", "currency": "TEXT",
         "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT", "currency_symbol": "TEXT"},
        all_block_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


# TODO: making it lookup the documentation before?
async def aggregate_transaction_transfers(blockchain: str, module: str, transaction_hash: str, sql_query: str):
    """
    Aggregate *individual transfers* within a transaction in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - address: target address of the transfer as text
        - currency: full currency name in lowercase. Prepended with module name and '/' if not-native currency
        - currency_symbol: currency symbol/ticker) in uppercase.
        - effect: amount in the smallest units as REAL type. Positive if gained, negative if spent.
        - failed: boolean indicating whether transaction failed
        - extra: special mark as text. 'f' for miner fee, 'b' for burnt fee, null for regular transfers
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
    unwrap_into_table(
        conn,
        {"address": "TEXT", "currency": "TEXT", "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT",
         "currency_symbol": "TEXT"},
        all_tx_events,
    )
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


# TODO: format times in API responses to be smaller so reducing it in schema for LLM easy to digest?
async def aggregate_address_mempool(blockchain: str, module: str, address: str, sql_query: str):
    """
    Aggregate *pending mempool transfers* for an address in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - transaction_hash: transaction hash as text
        - time: ISO timestamp of the mempool event as text
        - currency: full currency name in lowercase. Prepended with module name and '/' if not-native currency
        - currency_symbol: currency symbol/ticker) in uppercase.
        - effect: amount in the smallest units as REAL type. Positive if gained, negative if spent.
        - failed: boolean indicating whether transaction failed or null if not applicable
        - extra: special mark as text. 'f' for miner fee, 'b' for burnt fee, null for regular transfers
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
    unwrap_into_table(
        conn,
        {"transaction_hash": "TEXT", "time": "TEXT", "currency": "TEXT",
         "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT", "currency_symbol": "TEXT"},
        all_mempool_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


async def aggregate_address_balances(blockchain: str, module: str, address: str, sql_query: str):
    # TODO: real numbers here? Cuz is also inoperatable.
    """
    Aggregate *balance info* for an address in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and it contains following columns:
        - currency: full currency name in lowercase. Prepended with module name and `/` if not-native currency.
        - symbol: symbol in uppercase(ticker) - can be the same for multiple currencies, so check address or whether it's verified.
        - decimals: number of decimals of the currency.
        - balance: amount of currency on the balance in the smallest unit(that's why you need decimals).
            Stored as REAL type.
            Null if the currency is non-fungible.
        - is_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        in case if you query main module, there will be only row(example with `ethereum-main`):
        currency - "ethereum"
        symbol - "ETH"
        decimals - 18
        balance - "237558121960475169592"

        but when you query other modules, the currency will be in form of an address and prepended with module name:

        currency - "ethereum-erc-20/0xdAC...1ec7"
        symbol - "USDT"
        decimals - 18
        balance": "113231423123"

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
    print(all_balances, file=sys.stderr)
    unwrap_into_table(
        conn,
        {"currency": "TEXT", "symbol": "TEXT", "decimals": "INT", "balance": "REAL", "is_verified": "BOOLEAN"},
        all_balances
    )
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


async def aggregate_address_transfers(blockchain: str, module: str, address: str, sql_query: str):
    # TODO: is_verified.
    """
    Aggregate *confirmed individual transfers* for an address in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - block: block height as integer
        - transaction_hash: transaction hash as text
        - time: ISO timestamp of the event as text
        - currency: currency identifier. Lowercase name if native currency(e.g. `ethereum`, `bitcoin`)
            or contract address(in lowercase too) prepended with module name and separated by slash
            (e.g. ethereum-erc-20/0xda...c7(omitted for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - effect: amount in the smallest units as REAL type. Positive if gained, negative if spent.
        - failed: boolean indicating whether transaction failed
        - extra: special mark as text. 'f' for miner fee, 'b' for burnt fee, null for regular transfers
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
    # made number real, so LLM can operate on it without casting.
    # but it has a downside of decreased accuracy.
    unwrap_into_table(
        conn,
        {"block": "INT", "transaction_hash": "TEXT", "time": "TEXT", "currency": "TEXT",
         "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT", "currency_symbol": "TEXT"},
        all_address_events
    )
    aggregate = get_aggregate(conn, sql_query)
    return aggregate
