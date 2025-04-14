from mcp.server import FastMCP

from .address import get_address_overview
from .block import get_block_overview, get_latest_block
from .blockchain import detect_blockchains
from .ens import resolve_ens_domain
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
    ]:
        mcp_server.tool()(tool)
