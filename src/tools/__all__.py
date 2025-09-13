"""
Explicit exports for the tools package.
This file documents all available tools and their purposes.
"""

# Core blockchain tools
BLOCKCHAIN_TOOLS = [
    "detect_blockchains",
    "list_blockchains_and_modules",
]

# Address tools
ADDRESS_TOOLS = [
    "get_address_overview",
    "aggregate_address_balances",
    "aggregate_address_mempool", 
    "aggregate_address_transfers",
]

# Block tools
BLOCK_TOOLS = [
    "get_block_overview",
    "get_latest_block",
    "aggregate_block_transfers",
]

# Transaction tools
TRANSACTION_TOOLS = [
    "get_transaction_overview",
    "get_events_count_24h",
    "get_average_fee_24h_usd",
    "get_mempool_events_count",
    "aggregate_transaction_transfers",
]

# ENS tools
ENS_TOOLS = [
    "resolve_ens_domain",
]

# All available tools
ALL_TOOLS = (
    BLOCKCHAIN_TOOLS + 
    ADDRESS_TOOLS + 
    BLOCK_TOOLS + 
    TRANSACTION_TOOLS + 
    ENS_TOOLS
)

__all__ = ALL_TOOLS