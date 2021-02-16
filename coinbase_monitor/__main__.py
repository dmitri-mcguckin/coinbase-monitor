import os
import sys
import time
import json
import datetime as dt
import coinbase.wallet as cw
from coinbase.wallet.client import Client


__MARKET_HISTORY = os.path.expanduser('~/.cache/coinbase-monitor/'
                                      'market-history.json')
__CACHED_ACCOUNTS = os.path.expanduser('~/.cache/coinbase-monitor/'
                                       'accounts.json')
__BASE_CURRENCY = 'USD'
__UPDATE_HISTORY = dt.timedelta(minutes=10)
__EXCLUDED_CURRENCIES = ['XRP']
__INDICATED_CURRENCY = 'ATOM'
__LED_INDICATOR = False
__HW_CHECK = True


# Only import if the HW exists
if(__LED_INDICATOR):
    from .led import Led, \
                     init_hw, \
                     hw_check, \
                     set_indicator


def load_market_history() -> dict:
    try:
        with open(__MARKET_HISTORY, 'r') as file:
            return json.load(file)
    except OSError:
        return {}


def save_market_history(history: dict) -> None:
    with open(__MARKET_HISTORY, 'w+') as file:
        return json.dump(history, file, indent=4)


def update_market_history(client: cw.client.Client, history: dict) -> None:
    # Get the current exchange rates
    e_rates = client.get_exchange_rates()
    # Convert rates from str to float
    for k, v in e_rates.rates.items():
        e_rates.rates[k] = float(v)

    # Add to the history table
    history[int(dt.datetime.now().timestamp())] = {
        'currency': e_rates.currency,
        'rates': e_rates.rates
    }

    # Save to disk
    save_market_history(history)


def init_cache() -> bool:
    try:
        os.makedirs(os.path.dirname(__MARKET_HISTORY), exist_ok=True)
        os.makedirs(os.path.dirname(__CACHED_ACCOUNTS), exist_ok=True)
        return True
    except OSError:
        return False


def init_coinbase() -> cw.client.Client:
    token = os.environ.get('COINBASE_TOKEN')
    secret = os.getenv('COINBASE_SECRET')
    return Client(token, secret)


def get_active_accounts(client: cw.client.Client) -> [cw.model.Account]:
    return list(filter(lambda x: x.currency not in __EXCLUDED_CURRENCIES,
                       client.get_accounts()['data']))
# accounts = client.get_accounts()['data']
# return list(filter(lambda x: float(x['balance']['amount']) > 0, accounts))


def get_active_currencies(accounts: [cw.model.Account]) -> [str]:
    return list(map(lambda x: x.currency, accounts))


def get_exchange_delta(client: cw.client.Client,
                       currency: str,
                       history: dict) -> dict:
    now = dt.datetime.now().timestamp()
    ret = {}
    currency_pair = f'{currency}-{__BASE_CURRENCY}'
    rate_0 = float(client.get_sell_price(currency_pair=currency_pair).amount)

    for timestamp, rates in history.items():
        rates = rates.get('rates')
        timestamp = float(timestamp)
        elapsed = int(now - timestamp)
        rate_1 = 1 / rates.get(currency)
        ret[elapsed] = round(((rate_0 / rate_1) - 1) * 100, 2)
    return ret


def round_timedelta(delta: dt.timedelta) -> str:
    if(delta >= dt.timedelta(weeks=1)):
        return '+week'
    elif(delta >= dt.timedelta(days=1)):
        return '+day'
    elif(delta >= dt.timedelta(hours=1)):
        return '+hour'
    else:
        return f'+{int(delta.total_seconds() / 60)} minutes'


def main() -> None:
    # Initialize the cache dirs
    if(not init_cache()):
        print('There was a problem creating the cache directory!\nExiting'
              ' gracefully...')
        sys.exit(-1)

    # Initialize the HW stuff
    if(__LED_INDICATOR):
        leds = [Led.DOWN, Led.UP]
        init_hw(leds)
        if(__HW_CHECK):
            hw_check(leds)

    # Get coinbase info
    market_history = load_market_history()
    client = init_coinbase()
    accounts = get_active_accounts(client)
    currencies = get_active_currencies(accounts)
    currency_percs = {}

    # Check if there are any accounts with a balance
    if(len(accounts) == 0):
        print('No accounts with a positive balance!')
        sys.exit(0)

    # Create a market history cache if there is none
    if(len(market_history) == 0):
        print('No market history exists, creating now...')
        update_market_history(client, market_history)

    now = dt.datetime.now()
    updated = dt.datetime \
                .fromtimestamp(float(list(market_history.keys())[-1]))
    elapsed = dt.timedelta(seconds=(now.timestamp() - updated.timestamp()))

    print(f'Last update was {updated.ctime()}'
          f' ({int(elapsed.total_seconds() / 60)} minutes ago),')

    if(elapsed.total_seconds() > __UPDATE_HISTORY.total_seconds()):
        update_market_history(client, market_history)
    else:
        print(f'{int((__UPDATE_HISTORY - elapsed).total_seconds())}s until'
              ' next update!')

    # Display the deltas
    for c in sorted(currencies):
        deltas = get_exchange_delta(client, c, market_history)
        print(f'{c}:')
        currency_percs[c] = deltas
        for d, percentage in deltas.items():
            d = dt.timedelta(seconds=d)
            print(f'\t{round_timedelta(d)}: {"+" if percentage > 0 else ""}'
                  f'{percentage}%')

    # Toggle the indicator
    if(__LED_INDICATOR):
        ind_percs = currency_percs.get(__INDICATED_CURRENCY)
        if(ind_percs is not None):
            latest_perc = ind_percs[sorted(ind_percs.keys())[0]]
            led = Led.UP if latest_perc > 0 else Led.DOWN
            set_indicator(led)
        else:
            print(f'No percentages found for {__INDICATED_CURRENCY}')
            for _ in range(5):
                set_indicator(Led.UP)
                time.sleep(0.1)
                set_indicator(Led.DOWN)
