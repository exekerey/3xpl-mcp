from dotenv import load_dotenv
from httpx import AsyncClient
from mcp.server.fastmcp import FastMCP

load_dotenv()
client = AsyncClient(timeout=5)

mcp = FastMCP("3xpl")


@mcp.tool()
async def detect_string_blockchain(data: str) -> list[str]:
    """
    Detect a list of blockchains to which data string belongs to.

    Args:
        data (str): The string(address, transaction hash) to detect blockchains for.
    Returns (list[str]):
        A list of blockchains for which data string belongs to.
        May contain multiple blockchains.
    """

    response = await client.get(f"https://sandbox-api.3xpl.com/search?q={data}")
    response.raise_for_status()
    return response.json()['data']['results'].keys()


@mcp.tool()
async def resolve_ens_domain(domain: str) -> str:
    """
    Resolve an ENS domain(e.g. vitalik.eth) to a linked address in EVM blockchains.

    Args:
        domain (str): the domain for which to resolve the address.
    Returns (str):
        Returns linked address in EVM blockchains as a plain string.
        Example: 0xd8da...
    """
    response = await client.get(f"https://sandbox-api.3xpl.com/search?q={domain}")
    response.raise_for_status()
    blockchains_links = response.json()['data']['results']
    for blockchain, entity_link in blockchains_links.items():
        for entity, link in entity_link.items():
            return link.replace(f"https://3xpl.com/{blockchain}/{entity}/", "")

    return "This domain has no resolved address"


@mcp.tool()
async def get_address_information(blockchain: str, address: str) -> dict:
    """
    Get basic information about queried address in a particular blockchain.
    Args:
        blockchain (str): the single blockchain in which to search the address.
        address (str): the address in a blockchain to gather information about.
        Should be a plain address and not an ENS domain nor XPUB.
    Returns (dict):
        Return an information about balances and last transactions of an address.
    """
    response = await client.get(
        f"https://sandbox-api.3xpl.com/{blockchain}/address/{address}?data=balances,events&from=all&limit=1")
    response.raise_for_status()

    data = response.json()
    del data['context']
    return data


if __name__ == "__main__":
    import sys

    try:
        mcp.run(transport="stdio")
    except Exception as e:
        print(e, file=sys.stderr)
