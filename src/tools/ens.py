from src.core.connector import search_string


async def resolve_ens_domain(domain: str) -> str:
    search_results = await search_string(domain)
    blockchain_links = search_results.get('data', {}).get("results", {})

    for blockchain, entity_link in blockchain_links.items():
        for entity, link in entity_link.items():
            if entity != "address":
                break
            return link.replace(f"https://3xpl.com/{blockchain}/{entity}/", "")
    return "There is no addresses linked to this domain"
