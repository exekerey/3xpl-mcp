from src.core.connector import fetch_stats


async def list_blockchains_and_modules() -> dict:
    """
    Fetch all available blockchains and their modules in the API.
    Returns:
        dict: list of blockchains with their modules. Each module will have a description of it.
    """
    # TODO: there is a lot of repetition in response. Can extract main info so client LLM will spend less tokens.
    stats = await fetch_stats()
    library_blockchains = stats['library']['blockchains']
    library_modules = stats['library']['modules']
    blockchain_modules = {
        blockchain_name: {
            module: library_modules[module]['description']
            for module in blockchain_info['modules']
        }
        for blockchain_name, blockchain_info in library_blockchains.items()
    }

    return blockchain_modules
