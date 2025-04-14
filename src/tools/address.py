from src.core.connector import fetch_address
from src.core.utils import format_amount, reformat_time


async def get_address_overview(blockchain: str, address: str) -> str:
    """
    Get main information about an address in requested blockchain.
    :param blockchain: Lowercase blockchain name with dashes instead of spaces.
    :param address: A plain address to get information about. Must not be ENS domain.
    :return: Description with main details of provided address in provided blockchain,
    such as last transaction, number of pending transactions, balances in whitelisted tokens.
    """
    # TODO: clean up this mess.

    address_info = await fetch_address(blockchain, address)
    mempool_module_count = {module: len(transactions) for module, transactions in
                            address_info['data']['mempool'].items()}
    mempool_transactions_count = sum(mempool_module_count.values())
    last_transactions = [
        {"hash": transactions[0]['transaction'], "time": transactions[0]['time'], "module": module}
        for module, transactions in address_info['data']['events'].items() if transactions
    ]
    last_transaction = max(
        last_transactions,
        key=lambda transaction: transaction['time']
    ) if last_transactions else None

    if last_transaction is None:
        last_activity_text = "No transactions occurred for this address yet."
    else:
        last_activity_text = (
            f"Last transaction occurred at {reformat_time(last_transaction['time'])} "
            f"within the module `{last_transaction['module']}` "
            f"and had transaction hash {last_transaction['hash']}."
        )

    if mempool_transactions_count == 0:
        mempool_text = "There is no pending transactions for this address."
    else:
        mempool_text = f"There is {mempool_transactions_count} pending transactions for this address."

    # balances stuff
    modules_balances = address_info['data']['balances']
    currencies_info = address_info['library']['currencies']
    currency_amount = {currency: amount_events['balance']
                       for module, balances_amounts in modules_balances.items() if balances_amounts
                       for currency, amount_events in balances_amounts.items()}
    currencies_to_show = {currencies_info[currency]['symbol']: format_amount(currency_amount[currency],
                                                                             currencies_info[currency]['decimals'])
                          for currency, usd_price in address_info['library']['rates'].get('now', {}).items() if
                          usd_price['usd'] is not None}

    # showing zero values, for example stETH is 0 in vitalik.eth address
    if currencies_to_show:
        currencies_text = "This address has following verified tokens on balance: "
        for symbol, amount in currencies_to_show.items():
            currencies_text += f"\n- {amount} {symbol}"
    else:
        currencies_text = "This address has no whitelisted tokens."

    return f"""\
    \rThe {blockchain.capitalize()} address {address} has the following details:
    \r{currencies_text}
    \r{mempool_text}
    \r{last_activity_text}
    """


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(
        get_address_overview("bitcoin", "bc1qc8y5m888w8n94m7q7mpfwn30n6tm3p9xs93mkr")))
