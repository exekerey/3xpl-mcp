"""
Tests
For now they are just runners
"""
import asyncio
import time

from src.tools import aggregate_address_transfers, aggregate_address_mempool, aggregate_address_balances, \
    aggregate_transaction_transfers

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
