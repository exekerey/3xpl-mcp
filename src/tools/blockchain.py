from src.core.connector import search_string


async def detect_blockchains(data: str) -> [str]:
    """
    Detect blockchains of a data string.
    :param data: Data string to detect blockchains of. Can be an address, a transaction id or an ENS domain.
    :return: List of blockchains in which provided data string was found.
    """
    search_results = await search_string(data)
    blockchain_links = search_results.get('data', {}).get('results')
    if not blockchain_links:
        return []
    return list(blockchain_links.keys())
