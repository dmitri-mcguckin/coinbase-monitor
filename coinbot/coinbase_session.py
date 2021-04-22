from __future__ import annotations
import datetime as dt
from .price_history import Price
from coinbase.wallet.client import Client


class CoinbaseSession:
    def __init__(self: CoinbaseSession,
                 token: str,
                 secret: str,
                 crypto_symbols: [str] = [],
                 fiat_symbol: str = 'USD'):
        self.token = token
        self.secret = secret
        self.crypto_symbols = crypto_symbols
        self.fiat_symbol = fiat_symbol

    def __enter__(self: CoinbaseSession) -> CoinbaseSession:
        self.client = Client(self.token, self.secret)
        self.accounts = list(filter(lambda x: x.currency
                                    in self.crypto_symbols,
                                    self.client.get_accounts(limit=100).data))
        return self

    def __exit__(self: CoinbaseSession,
                 etype: str,
                 evalue: str,
                 traceback: any) -> None:
        pass

    def get_latest_price(self: CoinbaseSession, crypto_symbol: str) -> tuple:
        currency_pair = f'{crypto_symbol}-{self.fiat_symbol}'
        buy = self.client.get_buy_price(currency_pair=currency_pair)
        sell = self.client.get_sell_price(currency_pair=currency_pair)
        time = int(dt.datetime.now().timestamp())
        return (Price(buy.base, buy.currency, buy.amount, timestamp=time),
                Price(sell.base, sell.currency, sell.amount, timestamp=time))
