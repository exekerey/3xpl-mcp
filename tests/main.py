"""
Tests
For now they are just runners
"""
import asyncio
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.address_aggregates import aggregate_address_transfers, aggregate_address_mempool, aggregate_address_balances
from src.tools.transaction_aggregates import aggregate_transaction_transfers

loop = asyncio.new_event_loop()
print(loop.run_until_complete(
    aggregate_address_transfers("bitcoin", "bitcoin-main", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                                "select * from data limit 1")))
time.sleep(5)
print(
    loop.run_until_complete(
        aggregate_address_mempool(
            "ethereum", "ethereum-erc-20", "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
            "select * from data limit 1")
    )
)
time.sleep(5)
print(
    loop.run_until_complete(
        aggregate_address_balances(
            "bitcoin", "bitcoin-main", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "select * from data limit 1"
        )
    )
)
time.sleep(5)
print(
    loop.run_until_complete(
        aggregate_transaction_transfers(
            "bitcoin", "bitcoin-main", "34fa72fc6705f5b4db83632dde655b723ce1cceee1ef0afdf1ed6e477bd8f1fa",
            "select * from data limit 1"
        )
    )
)
