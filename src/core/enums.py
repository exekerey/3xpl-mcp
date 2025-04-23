from enum import Enum


class AddressDataSource(Enum):
    mempool = "mempool"
    events = "events"
    balances = "balances"
