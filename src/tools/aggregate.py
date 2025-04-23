import functools

from src.core.connector import fetch_block_events, fetch_transaction_events, fetch_address_data, \
    fetch_address_balances
from src.core.db import unwrap_into_table, setup_sqlite_connection, get_aggregate
from src.core.enums import AddressDataSource
from src.core.utils import collect_all_pages


# current state of actions:
#  test each tool with Claude, see if it runs, get some edge cases

# todo: dynamic extra. Different blockchains have different extras.
# todo: tune tool descriptions better - few issues:
#           - not using is_verified when checking balances
#           - not passing modules correctly unless provided with exact module name
#           (need to make it to look up modules though?)

# TODO: segmenting on an address transfers.
#  For example allowing inputting 30 days range and querying stuff on this range.
#  And then aggregating.
#  upd: non-trivial feature. Might require O(segments + page(segment_i)) of requests

# TODO: when going out of allowed range for pages, notifying LLM about boundaries.
#   for example telling the time of first event

# todo: docstrings actually can be assigned separately:
#  `fn.__doc__ = "description"` and this could be reducing some duplication.
#  so having modularizing descriptions based on fields, and pasting that via formatting if it's needed for the tool.


async def aggregate_block_transfers(blockchain: str, module: str, height: int, sql_query: str):
    """
    Aggregate *individual transfers* within a block in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and contains the following columns:
        - transaction_hash: transaction hash as text
        - address: target address of the transfer as text
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - currency_decimals: number of decimals for the currency. 0 if the currency is indivisible(nft).
        - currency_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        - effect: amount in the smallest units as REAL type. Positive if the address is receiver, negative if is sender.
        - failed: boolean indicating whether transaction failed
        - extra: Special marker describing the type of transfer as tet field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
            NOTICE: in UTXO blockchains transfers extra will be always null. Here are other traits of transfers:
            - in UTXO blockchains, miner fee(including block reward) will be the sum of transfers where special address `the-void` is receiver.
            - block reward is the transfer where special address `the-void` is sender. Keep in mind that this also includes the miner fees.
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
        {"transaction_hash": "TEXT", "address": "TEXT", "currency_id": "TEXT",
         "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT", "currency_symbol": "TEXT",
         "currency_verified": "BOOLEAN", "currency_decimals": "TINYINT", "exchange_rate": "REAL"},
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
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - currency_decimals: number of decimals for the currency. 0 if the currency is indivisible(nft).
        - currency_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        - effect: amount in the smallest units as REAL type. Positive if the address is receiver, negative if is sender.
        - failed: boolean indicating whether transaction failed
        - extra: Special marker describing the type of transfer as tet field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
            NOTICE: in UTXO blockchains transfers extra will be always null. Here are other traits of transfers:
            - in UTXO blockchains, miner fee(including block reward) will be the sum of transfers where special address `the-void` is receiver.
            - block reward is the transfer where special address `the-void` is sender. Keep in mind that this also includes the miner fees.
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
        {"address": "TEXT", "currency_id": "TEXT", "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT",
         "currency_symbol": "TEXT", "currency_verified": "BOOLEAN", "currency_decimals": "TINYINT",
         "exchange_rate": "REAL"},
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
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - currency_decimals: number of decimals for the currency. 0 if the currency is indivisible(nft).
        - currency_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        - effect: amount in the smallest units as REAL type. Positive if the address is receiver, negative if is sender.
        - failed: boolean indicating whether transaction failed or null if not applicable
        - extra: Special marker describing the type of transfer as tet field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
            NOTICE: in UTXO blockchains transfers extra will be always null. Here are other traits of transfers:
            - in UTXO blockchains, miner fee(including block reward) will be the sum of transfers where special address `the-void` is receiver.
            - block reward is the transfer where special address `the-void` is sender. Keep in mind that this also includes the miner fees.    Args:
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
        {"transaction_hash": "TEXT", "time": "TEXT", "currency_id": "TEXT",
         "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT", "currency_symbol": "TEXT",
         "currency_verified": "BOOLEAN", "currency_decimals": "TINYINT", "exchange_rate": "REAL"},
        all_mempool_events)
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


async def aggregate_address_balances(blockchain: str, module: str, address: str, sql_query: str):
    """
    Aggregate *balance info* for an address in requested blockchain within requested module in a sqlite table.
    Schema:
        table is called data and it contains following columns:
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - symbol: symbol in uppercase(ticker) - can be the same for multiple currencies, so check address or whether it's verified.
        - decimals: number of decimals of the currency.
        - balance: amount of currency on the balance in the smallest unit(that's why you need decimals).
            Stored as REAL type.
            Null if the currency is non-fungible.
        - is_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        in case if you query main module, there will be only row(example with `ethereum-main`):
        currency - "ethereum"
        symbol - "ETH"
        decimals - 18
        balance - "237558121960475169592"
        etc...

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
    unwrap_into_table(
        conn,  # TODO: renaming decimals -> currency decimals as in others?
        {"currency_id": "TEXT", "symbol": "TEXT", "decimals": "INT", "balance": "REAL", "is_verified": "BOOLEAN",
         "exchange_rate": "REAL"},
        all_balances
    )
    aggregate = get_aggregate(conn, sql_query)
    return aggregate


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
        - extra: Special marker describing the type of transfer as tet field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
            NOTICE: in UTXO blockchains transfers extra will be always null. Here are other traits of transfers:
            - in UTXO blockchains, miner fee(including block reward) will be the sum of transfers where special address `the-void` is receiver.
            - block reward is the transfer where special address `the-void` is sender. Keep in mind that this also includes the miner fees.
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
        {"block": "INT", "transaction_hash": "TEXT", "time": "TEXT", "currency_id": "TEXT",
         "effect": "REAL", "failed": "BOOLEAN", "extra": "TEXT", "currency_symbol": "TEXT",
         "currency_verified": "BOOLEAN", "currency_decimals": "TINYINT", "exchange_rate": "REAL"},
        all_address_events
    )
    aggregate = get_aggregate(conn, sql_query)
    return aggregate
