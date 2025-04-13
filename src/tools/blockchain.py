from src.core.connector import search_string


async def detect_blockchains(data: str):
    search_results = await search_string(data)
    blockchain_links = search_results.get('data', {}).get('results')
    if not blockchain_links:
        return []
    return blockchain_links.keys()
