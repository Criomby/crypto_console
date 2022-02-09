import requests
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from pycoingecko import CoinGeckoAPI
import pandas as pd
from datetime import datetime


class CoingeckoStats:

    def __init__(self):
        self.CG = CoinGeckoAPI()
        self.df_coin_prices_eur = pd.DataFrame()
        self.global_data = self.CG.get_global()

    def api_call(self):
        try:
            url = 'https://api.coingecko.com/api/v3/ping'
            headers = {
                'Accepts': 'application/json',
            }
            session = Session()
            session.headers.update(headers)
            response = session.get(url)
            return response
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return e

    def coins(self):
        data = self.CG.get_coins_markets(
            vs_currency='eur',
            per_page=10,
            price_change_percentage='7d',
        )
        df = pd.DataFrame.from_dict(data)
        df = df[['name', 'symbol', 'current_price', 'market_cap_rank', 'price_change_percentage_24h',
                 'price_change_percentage_7d_in_currency']]
        df = df.rename(columns={
            'current_price': 'price_€',
            'market_cap_rank': 'rank',
            'price_change_percentage_24h': '24h_change_%',
            'price_change_percentage_7d_in_currency': 'curr_7d_change_%',
        }).round(decimals=2)
        df.set_index('name', inplace=True)
        df = df.rename_axis(None)
        data_mcf = self.market_cap_percentage()
        df['mkt_cap_%'] = data_mcf['mkt_cap_%'].values
        df = df[['symbol', 'price_€', 'rank', 'mkt_cap_%', '24h_change_%', 'curr_7d_change_%']]
        self.df_coin_prices_eur = df[['price_€']]
        return df

    def coins_11to20(self):
        data = self.CG.get_coins_markets(
            vs_currency='eur',
            per_page=20,
            price_change_percentage='7d',
        )
        df = pd.DataFrame.from_dict(data)
        df = df[['name', 'symbol', 'current_price', 'market_cap_rank', 'price_change_percentage_24h',
                 'price_change_percentage_7d_in_currency']]
        df = df.rename(columns={
            'current_price': 'price_€',
            'market_cap_rank': 'rank',
            'price_change_percentage_24h': '24h_change_%',
            'price_change_percentage_7d_in_currency': 'curr_7d_change_%',
        }).round(decimals=2)
        df.set_index('name', inplace=True)
        df = df.rename_axis(None)
        df = df.iloc[[10, 11, 12, 13, 14]]
        df['mkt_cap_%'] = ['na' for i in range(5)]
        return df

    def market_cap_change_percentage_24h_usd(self):
        data = self.global_data['market_cap_change_percentage_24h_usd'] / 100
        return '{0:.2%}'.format(data)

    def market_cap_percentage(self):
        data = self.global_data['market_cap_percentage']
        df = pd.DataFrame(data.items())
        df = df.rename(columns={0: 'symbol', 1: 'mkt_cap_%'}).round(decimals=2)
        df.set_index('symbol', inplace=True)
        df = df.rename_axis(None)
        return df

    def total_market_cap(self):
        data = self.global_data['total_market_cap']['eur'] / 1000000000000
        return round(data, 2)

    def trending(self):
        data = self.CG.get_search_trending()
        data = data['coins']
        df_data = pd.DataFrame()
        for i in range(0, len(data), 1):
            item = data[i]
            coin = item
            df = pd.DataFrame(coin.values())
            df_data = pd.concat([df_data, df])
        df_data_display = df_data[['symbol', 'name', 'price_btc', 'market_cap_rank']]
        df_data_display.set_index('symbol', inplace=True)
        df_data_display = df_data_display.rename_axis(None)
        return df_data_display


class EtherGasStats:

    def __init__(self):
        self.url = 'http://ethgas.watch/api/gas'
        headers = {
            'Accepts': 'application/json',
        }

        self.session = Session()
        self.session.headers.update(headers)
        self.response = dict()

    def api_call(self):
        try:
            self.response = self.session.get(self.url)
            return self.response
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return e

    def get_eth_gas_stats(self):
        data = json.loads(self.response.text)
        stats = pd.DataFrame(data, columns=['slow', 'normal', 'fast', 'instant'])
        return stats


class CurrencyConversion:
    def __init__(self):
        # insert your api key into the url
        self.url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey=*insert_api_key*'
        headers = {
            'Accepts': 'application/json',
        }
        self.session = Session()
        self.session.headers.update(headers)

        self.response = dict()
        self.rate = float()

    def api_call(self):
        try:
            self.response = self.session.get(self.url)
            return self.response
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return e

    def get_fx_rate(self):
        data = json.loads(self.response.text)
        self.rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        return self.rate


def get_datetime():
    now = datetime.now()
    return now.strftime("%d.%m.%Y %H:%M:%S")


def check_internet_connection(host='https://duckduckgo.com/'):
    try:
        requests.get(host, timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def check_api_status(response):
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        return "Error: " + str(e)
