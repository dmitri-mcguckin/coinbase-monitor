from . import COINBASE_TOKEN, COINBASE_SECRET
from coinbase.wallet.client import Client


def main() -> None:
    print(f'Using token: {COINBASE_TOKEN} with secret: {COINBASE_SECRET}')

    # client = Client(api_token, api_secret)
