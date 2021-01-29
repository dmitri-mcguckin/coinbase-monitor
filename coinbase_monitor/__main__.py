import os
from coinbase.wallet.client import Client


def main() -> None:
    token = os.environ.get('COINBASE_TOKEN')
    secret = os.getenv('COINBASE_SECRET')
    client = Client(token, secret)

    accounts = client.get_accounts()
    print(f'Accounts: {accounts}')

    notifications = client.get_notifications()
    print('Notifications:')
    for n in notifications:
        print(f'{n}')
