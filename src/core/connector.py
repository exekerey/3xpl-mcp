from typing import Optional

from src.core.client import client
from src.core.config import config
from src.core.enums import AddressDataSource


# removing `context` field from each request would be nice for keeping response clean.
# UPD: pointless, as I don't pass the whole response to LLM.
async def fetch_stats(blockchain: Optional[str] = None):
    params = {
        "from": "all" if blockchain is None else blockchain,
        "library": "blockchains,modules"
    }
    response = await client.get(
        f"{config.threexpl_api_base_url}/",
        params=params
    )
    response.raise_for_status()
    return response.json()


async def search_string(data: str):
    params = {
        "q": data
    }
    response = await client.get(
        f"{config.threexpl_api_base_url}/search",
        params=params
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
        f"{config.threexpl_api_base_url}/{blockchain}/address/{address}",
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
        "mixins": "stats"
    }
    response = await client.get(
        f"{config.threexpl_api_base_url}/{blockchain}/transaction/{transaction_hash}",
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
        f"{config.threexpl_api_base_url}/{blockchain}/block/{height}",
        params=params
    )
    response.raise_for_status()
    return response.json()


async def fetch_block_events(blockchain: str, module: str, height: int, limit: int = 1000, page: int = 0):
    params = {
        "data": "events",
        "limit": limit,
        "page": page,
        "from": module,
        "library": "currencies",
    }
    response = await client.get(
        f"{config.threexpl_api_base_url}/{blockchain}/block/{height}",
        params=params,
    )
    response.raise_for_status()
    return response.json()


async def fetch_transaction_events(blockchain: str, module: str, transaction_hash: str,
                                   limit: int = 1000, page: int = 0):
    params = {
        "data": "events",
        "limit": limit,
        "page": page,
        "from": module,
        "library": "currencies"
    }

    response = await client.get(
        f"{config.threexpl_api_base_url}/{blockchain}/transaction/{transaction_hash}",
        params=params,
    )
    response.raise_for_status()
    return response.json()


# can be multiple separated, or can be merged though.
async def fetch_address_data(blockchain: str, module: str, address: str, source: AddressDataSource,
                             limit: int = 1000, page: int = 0):
    params = {
        "data": source.value,
        "limit": limit,
        "page": page,
        "from": module,
        "library": "currencies,rates(usd)",
    }

    response = await client.get(
        f"{config.threexpl_api_base_url}/{blockchain}/address/{address}",
        params=params,
    )
    response.raise_for_status()
    return response.json()


async def fetch_address_balances(blockchain: str, module: str, address: str, source: AddressDataSource,
                                 limit: int = 1000, page: int = 0):
    # limit doesn't work at balances
    address_data = await fetch_address_data(blockchain, module, address, source, limit, page)
    balances = address_data['data']['balances'][module]
    currencies_library = address_data['library']['currencies']
    rates_library = address_data['library']['rates']['now']

    unwrapped_balance_data = []
    if not balances:
        return unwrapped_balance_data
    for currency, currency_info in balances.items():
        unwrapped_balance_data.append({
            "currency": currency,
            "symbol": currencies_library[currency]["symbol"],
            "decimals": currencies_library[currency]["decimals"],
            "balance": currency_info['balance'],
            "is_verified": rates_library[currency]['usd'] is not None
        })

    return unwrapped_balance_data


if __name__ == "__main__":
    import asyncio

    # print(asyncio.run(fetch_stats("bitcoin")))
    print(asyncio.run(fetch_address("bitcoin", "19dENFt4wVwos6xtgwStA6n8bbA57WCS58")))
