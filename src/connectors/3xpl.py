from httpx import AsyncClient

from src.core.config import config

client = AsyncClient(timeout=5)  # reusable client


async def fetch_stats(blockchain: str):
    response = await client.get(
        f"{config.txpl_api_base_url}/?from={blockchain}")
    return response.json()


async def search_string(data: str):
    response = await client.get(
        f"{config.txpl_api_base_url}/search?q={data}"
    )
    return response.json()


async def fetch_transaction(blockchain: str, transaction_hash: str):
    ...
