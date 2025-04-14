from src.core.connector import fetch_stats, fetch_block
from src.core.utils import reformat_time


async def get_block_overview(blockchain: str, height: int):
    """
    Get main information about a block in requested blockchain.
    :param blockchain: Lowercase blockchain name with dashes instead of spaces.
    :param height: The height of the requested block.
    :return: Description with main details about requested block within provided blockchain.
    Details include number of confirmations, block hash, block time and number of individual transfers within the block.
    """
    block_info = await fetch_block(blockchain, height)

    best_block = block_info['mixins']['stats'][blockchain]['best_block']
    if best_block < height:
        return f"The {blockchain.capitalize()} block {height} hasn't been processed yet."
    block_timestamp = reformat_time(block_info['data']['block']['time'])

    block_events = block_info['data']['block']['events']
    block_hash = block_info['data']['block']['hash']

    block_events_verbal = [f"{no_events if no_events else 0} events in {module} module" for module, no_events in
                           block_events.items()]
    return f"""\
    \rThe {blockchain.capitalize()} block {height} has the following details:
    \r - {best_block - height} confirmations.
    \r - block hash is {block_hash}.
    \r - block timestamp is {block_timestamp}.
    \r - the block has following count of individual transfers(not whole transactions):
    \r    + {'\n \t+ '.join(block_events_verbal)}
    """


async def get_block_info(blockchain: str, height: int):
    block_info = await fetch_block(blockchain, height)
    return block_info


async def get_latest_block(blockchain: str):
    """
    Fetch the height(block id) of the latest(best) block in the requested blockchain.
    :param blockchain: Lowercase blockchain name with dashes instead of spaces.
    :return: Returns a number which is the latest block id in the provided blockchain.
    """
    stats = await fetch_stats(blockchain)
    return stats['data']['blockchains'][blockchain]['best_block']  # add time?


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_block_overview("ethereum", 22251555)))
