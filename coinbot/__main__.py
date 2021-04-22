import os
import datetime as dt
from matplotlib import pyplot as plt
from . import PRICE_HISTORY_DB, API_UPDATE_INTERVAL
from .coinbase_session import CoinbaseSession
from .price_history import PriceHistory


def main():
    token = os.environ.get('COINBASE_TOKEN')
    secret = os.environ.get('COINBASE_SECRET')

    with PriceHistory(PRICE_HISTORY_DB, 'buy_prices') as buy_prices, \
         PriceHistory(PRICE_HISTORY_DB, 'sell_prices') as sell_prices, \
         CoinbaseSession(token, secret) as cs:
        newest = buy_prices.newest
        last_update = dt.datetime.fromtimestamp(newest.timestamp) \
            if(newest is not None) \
            else dt.datetime.now()

        plt.ioff()  # Disable interactive mode
        plt.show()  # Open the plot window

        elapsed = int((dt.datetime.now() - last_update).total_seconds())
        if(elapsed > 0):
            print(f'Last known update was: {last_update.ctime()}'
                  f' or {elapsed}s ago.')
        else:
            print('No history found!')

        # Start the event loop
        while(True):
            now = dt.datetime.now()

            # Update if it's time
            if((now - last_update) >= API_UPDATE_INTERVAL):
                latest = cs.get_latest_price('BTC')
                buy_prices.add(latest[0])
                sell_prices.add(latest[1])
                last_update = dt.datetime.now()
                print(f'[{last_update.ctime()}]: Fetching latest prices...')

                for d in [(dt.timedelta(seconds=31), 'Latest'),
                          (dt.timedelta(minutes=1), '1m'),
                          (dt.timedelta(hours=1), '1h'),
                          (dt.timedelta(days=1), '1d'),
                          (dt.timedelta(weeks=1), '1w')]:
                    bdelta = buy_prices.delta(d[0])
                    sdelta = sell_prices.delta(d[0])
                    if(bdelta and sdelta):
                        print(f'\t[{d[1]}] (Buy Δ: {bdelta}%)'
                              f' (Sell Δ: {sdelta}%)')

            # Plot histories
            for hist in [(buy_prices, 'g-'), (sell_prices, 'r-')]:
                x = list(map(lambda x: dt.datetime.fromtimestamp(x.timestamp),
                             hist[0]))
                y = list(map(lambda x: x.value, hist[0]))
                plt.plot(x, y, hist[1])

            # Wait for a bit
            plt.pause(API_UPDATE_INTERVAL.total_seconds() / 10)


if __name__ == '__main__':
    main()
