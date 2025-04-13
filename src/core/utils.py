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


if __name__ == '__main__':
    print(format_amount(12182, 18))
