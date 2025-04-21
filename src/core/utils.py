from datetime import datetime
from decimal import Decimal, getcontext

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

        if get_currency_info:
            currency_library = data['library']['currencies']
            rates_library = data['library']['rates']

            if rates_library.get('now'):
                rates = rates_library['now']
            else:
                rates = {}
                for _, rate_info in rates_library.items():
                    rates.update(rate_info)

            for data_chunk in required_data:
                data_chunk['currency_symbol'] = currency_library[data_chunk['currency']]['symbol']

                # maybe instead of verification - provide rate? Rate at the time of the transaction

                data_chunk['currency_verified'] = True if rates[data_chunk['currency']]['usd'] is not None else False

        all_pages.extend(required_data)

        if stop_after_first or current_page > 10:
            break

        current_page += 1
    return all_pages


if __name__ == '__main__':
    print(format_amount(12182, 18))
