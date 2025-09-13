"""
Shared schema definitions and utilities for aggregate tools.
"""
from typing import Dict, Any

# Common database schema for transfers
TRANSFERS_SCHEMA: Dict[str, str] = {
    "transaction_hash": "TEXT",
    "address": "TEXT", 
    "currency_id": "TEXT",
    "currency_symbol": "TEXT",
    "currency_decimals": "TINYINT",
    "currency_verified": "BOOLEAN",
    "exchange_rate": "REAL",
    "effect": "REAL",
    "failed": "BOOLEAN",
    "extra": "TEXT"
}

# Schema for balances
BALANCES_SCHEMA: Dict[str, str] = {
    "currency": "TEXT",
    "symbol": "TEXT", 
    "decimals": "TINYINT",
    "balance": "REAL",
    "is_verified": "BOOLEAN"
}

def get_transfer_schema_description() -> str:
    """Get standardized schema description for transfer tables."""
    return """
    Schema:
        table is called data and contains the following columns:
        - transaction_hash: transaction hash as text
        - address: target address of the transfer as text
        - currency_id: currency identifier in lowercase. Can be native currency name (e.g. `ethereum`, `bitcoin`)
            or contract address prefixed with the module name and separated by a slash
            (e.g. `ethereum-erc-20/0xda...c7` (address shortened for simplicity)
        - currency_symbol: currency symbol/ticker) in uppercase.
        - currency_decimals: number of decimals for the currency. 0 if the currency is indivisible(nft).
        - currency_verified: boolean indicating whether the currency is widely accepted and listed on major exchanges(indicates that a currency is not a scam or copy)
        - exchange_rate: exchange rate for the currency in USD. Null if the currency is not listed anywhere yet.
        - effect: amount in the smallest units as REAL type. Positive if the address is receiver, negative if is sender.
        - failed: boolean indicating whether transaction failed
        - extra: Special marker describing the type of transfer as text field. Possible values:
            'r' for block reward
            'f' for miner fee
            'b' for burnt fee
            'i' for uncle inclusion reward
            'u' for uncle reward
            'c' for contract creation
            'd' for contract destruction
            null for Regular/ordinary transfer (no special type)
            NOTICE: in UTXO blockchains transfers extra will be always null. Here are other traits of transfers:
            - in UTXO blockchains, miner fee(including block reward) will be the sum of transfers where special address `the-void` is receiver.
            - block reward is the transfer where special address `the-void` is sender. Keep in mind that this also includes the miner fees.
    """

def get_balance_schema_description() -> str:
    """Get standardized schema description for balance tables."""
    return """
    Schema:
        table is called data and contains the following columns:
        - currency: currency identifier
        - symbol: currency symbol/ticker
        - decimals: number of decimals for the currency
        - balance: balance amount in the smallest units  
        - is_verified: boolean indicating whether the currency is verified/whitelisted
    """