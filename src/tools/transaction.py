from src.core.connector import fetch_transaction, fetch_stats
from src.core.utils import reformat_time


async def get_transaction_info(blockchain: str, transaction_hash: str):
    transaction_info = await fetch_transaction(blockchain, transaction_hash)
    return transaction_info


async def get_transactions_count_24h(blockchain: str):
    stats = await fetch_stats(blockchain)
    return stats['data']['blockchains'][blockchain]['events_24h']


async def get_transaction_fee_24h_usd(blockchain: str):
    stats = await fetch_stats(blockchain)
    return stats['data']['blockchains'][blockchain]['average_fee_24h']['usd']


async def get_mempool_transactions_count(blockchain: str):
    stats = await fetch_stats(blockchain)
    return stats['data']['blockchains'][blockchain]['mempool_events']


async def get_transaction_overview(blockchain: str, transaction_hash: str):
    transaction_info = await fetch_transaction(blockchain, transaction_hash)
    best_block = transaction_info['mixins']['stats'][blockchain]['best_block']
    included_block = transaction_info['data']['transaction']['block']
    transaction_time = reformat_time(transaction_info['data']['transaction']['time'])
    module_events_text = ""
    for module, events_count in transaction_info['data']['transaction']['events'].items():
        if events_count == 0:
            continue
        module_events_text += f"\n- module `{module}` has {events_count} transfers"

    return f"""\
    \rThe {blockchain.capitalize()} transaction {transaction_hash} has the following details:
    \rIt was included in {included_block} at {transaction_time} and has {best_block - included_block} confirmations.
    \rThis transaction has following count of transfers in it: {module_events_text}
    """


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(
        get_transaction_overview("ethereum", "0xa0ea1fdfa80da777fbc3a4dcf68e789de2d60b7aa079c3399e08c872e7283ff4")))
