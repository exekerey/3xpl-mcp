from collections import defaultdict
from datetime import datetime
from decimal import Decimal, getcontext

from src.core.config import config

getcontext().prec = 30


def format_amount(currency_amount, currency_decimals):
    decimals_amount = Decimal(currency_amount) / Decimal(10 ** currency_decimals)
    s = format(decimals_amount.normalize(), 'f')
    if '.' not in s:
        return s
    int_part, frac_part = s.split('.')
    i = 0
    count = 0
    while i < len(frac_part) and count < 2:
        if frac_part[i] != '0':
            count += 1
        i += 1
    return int_part + '.' + frac_part[:i] if i > 0 else int_part


def reformat_time(time_string: str) -> str:
    timestamp = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


async def collect_all_pages(async_fetcher, data_keys: list[str], get_currency_info: bool,
                            stop_after_first: bool) -> list:
    all_pages = []
    current_page = 0
    while True:
        data = await async_fetcher(page=current_page)

        required_data = data
        for key in data_keys:
            required_data = required_data[key]
            if not required_data:
                break

        if not required_data:
            break

        if get_currency_info:
            currency_library = data['library']['currencies']
            rates_library = data['library']['rates']

            currency_timestamp_rates = defaultdict(dict)  # {ethereum: {now: 123123, 2077-12-12: 12314123}}
            for timestamp, currencies_rates in rates_library.items():
                for currency, rate_info in currencies_rates.items():
                    # fiat_ticker = list(rate_info.keys())[0]
                    currency_timestamp_rates[currency].update({timestamp: rate_info})

            for data_chunk in required_data:
                currency_id = data_chunk['currency']

                data_chunk['currency_symbol'] = currency_library[currency_id]['symbol']
                data_chunk['currency_decimals'] = currency_library[currency_id]['decimals']

                # different processing of rates depending on the endpoint:
                #  - blocks - get from first date, no dates in events.
                #  - balances - get from `now`, no dates in events.
                #  - address transactions/mempool - get from rates from according timestamp from event itself.
                if currency_timestamp_rates[currency_id]:
                    data_chunk['currency_verified'] = True

                    if data_chunk.get('time'):  # or not data_chunk.get('block'):
                        data_chunk['exchange_rate'] = currency_timestamp_rates[currency_id][data_chunk['time']]['usd']
                    elif not data_chunk.get('block'):
                        if data['data'].get('block'):
                            timestamp = data['data']['block']['time']
                        elif data['data'].get('transaction'):
                            timestamp = data['data']['transaction']['time']
                        else:
                            raise ValueError()
                        data_chunk['exchange_rate'] = \
                            currency_timestamp_rates[currency_id][timestamp]['usd']
                    else:
                        data_chunk['exchange_rate'] = currency_timestamp_rates[currency_id]['now']['usd']
                else:
                    data_chunk['currency_verified'] = False

        for data_chunk in required_data:
            if "transaction" not in data_chunk:
                break
            data_chunk['transaction_hash'] = data_chunk['transaction']
            del data_chunk['transaction']

        all_pages.extend(required_data)

        if stop_after_first or current_page > config.pagination_limit:
            break

        current_page += 1
    return all_pages


if __name__ == '__main__':
    print(format_amount(12182, 18))
