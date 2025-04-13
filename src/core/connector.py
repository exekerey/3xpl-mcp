from src.core.client import client
from src.core.config import config


# todo: removing context from each request would be nice for keeping context clean.
async def fetch_stats(blockchain: str):
    response = await client.get(
        f"{config.txpl_api_base_url}/?from={blockchain}")
    response.raise_for_status()
    return response.json()


async def search_string(data: str):
    response = await client.get(
        f"{config.txpl_api_base_url}/search?q={data}"
    )
    response.raise_for_status()
    return response.json()


async def fetch_address(blockchain: str, address: str, use_case: str = "address_overview"):
    params = {
        "data": "address,events",
        "limit": 1000,
        # "page": 0,
        "from": "all",
        "library": "currencies,rates(usd)"
    }
    if use_case == "segment_lookup":
        # balances and mempool can not be used with segment
        # as well as `page` has to be provided.
        params['segment'] = "?some segment"
    elif use_case == "address_overview":
        params["data"] += ",balances,mempool,kya"
    else:
        raise ValueError("unknown use_case")

    response = await client.get(
        f"{config.txpl_api_base_url}/{blockchain}/address/{address}",
        params=params,
    )
    response.raise_for_status()
    return response.json()


async def fetch_transaction(blockchain: str, transaction_hash: str):
    params = {
        "data": "transaction,events,kyt,special",
        "from": "all",
        "limit": 1000,  # too high limit though
        "page": 0,
    }
    response = await client.get(
        f"{config.txpl_api_base_url}/{blockchain}/address/{transaction_hash}",
        params=params
    )
    response.raise_for_status()

    return response.json()


async def fetch_block(blockchain: str, height: int):
    params = {
        "data": "block,events",
        "limit": 1000,  # iterate through?
        "from": "all",
        "mixins": "stats",
    }
    response = await client.get(
        f"{config.txpl_api_base_url}/{blockchain}/block/{height}",
        params=params
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    import asyncio

    # print(asyncio.run(fetch_stats("bitcoin")))
    print(asyncio.run(fetch_address("bitcoin", "19dENFt4wVwos6xtgwStA6n8bbA57WCS58")))
