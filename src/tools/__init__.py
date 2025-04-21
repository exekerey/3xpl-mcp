from mcp.server import FastMCP

from .address import get_address_overview
from .aggregate import aggregate_block_transfers, aggregate_address_mempool, aggregate_address_balances, \
    aggregate_address_transfers, aggregate_transaction_transfers
from .block import get_block_overview, get_latest_block
from .blockchain import detect_blockchains
from .ens import resolve_ens_domain
from .modules import list_blockchains_and_modules
from .transaction import get_transaction_overview, get_transactions_count_24h, get_mempool_transactions_count, \
    get_transaction_fee_24h_usd


def init_tools(mcp_server: FastMCP):
    for tool in [
        get_address_overview,
        get_block_overview,
        get_latest_block,
        detect_blockchains,
        resolve_ens_domain,
        get_transaction_overview,
        get_transactions_count_24h,
        get_mempool_transactions_count,
        get_transaction_fee_24h_usd,
        aggregate_block_transfers,
        aggregate_transaction_transfers,
        aggregate_address_balances,
        aggregate_address_mempool,
        aggregate_address_transfers,
        list_blockchains_and_modules,
    ]:
        mcp_server.tool()(tool)
