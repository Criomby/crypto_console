import requests
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from pycoingecko import CoinGeckoAPI
import pandas as pd
from datetime import datetime

# i.c.w run.__VERSION__ = '2.2.1'


class CoingeckoStats:
    # open API, no key required, 50 calls / min.
    def __init__(self):
        self.CG = CoinGeckoAPI()
        # to store coin prices for calculation of prices of other coins given in btc by api
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
            # uncomment the following line and define names to get desired coins
            # ids=['bitcoin', 'ethereum', 'ripple', 'decentraland'],
            # following line gets the defined number of coins by rank from 1 to n
            per_page=10,
            price_change_percentage='7d',
        )
        df = pd.DataFrame.from_dict(data)
        # print(df)
        df = df[['name', 'symbol', 'current_price', 'market_cap_rank', 'price_change_percentage_24h',
                 'price_change_percentage_7d_in_currency']]
        df = df.rename(columns={
            'current_price': 'price (€)',
            'market_cap_rank': 'rank',
            'price_change_percentage_24h': '24hChange%',
            'price_change_percentage_7d_in_currency': '7dChange%',
        }).round(decimals=2)
        df.set_index('name', inplace=True)
        df = df.rename_axis(None)
        # add column mkt_cap_% to coins df
        data_mcf = self.market_cap_percentage()
        df['mktCap%'] = data_mcf['mktCap%'].values
        df = df[['symbol', 'price (€)', 'rank', 'mktCap%', '24hChange%', '7dChange%']]
        self.df_coin_prices_eur = df[['price (€)']]
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
            'current_price': 'price (€)',
            'market_cap_rank': 'rank',
            'price_change_percentage_24h': '24hChange%',
            'price_change_percentage_7d_in_currency': '7dChange%',
        }).round(decimals=2)
        df.set_index('name', inplace=True)
        df = df.rename_axis(None)
        # specify number of additional rows for 'coin stats'
        df = df.iloc[[10, 11, 12, 13, 14]]
        # no mkt_cap_% data available for coins after rank 10
        # avoid NaN values
        df['mktCap%'] = ['na' for i in range(5)]
        return df

    def market_cap_change_percentage_24h_usd(self):
        # extract 'market_cap_change_percentage_24h_usd'
        data = self.global_data['market_cap_change_percentage_24h_usd'] / 100
        return '{0:.2%}'.format(data)

    def market_cap_percentage(self):
        # extract market_cap_percentage
        data = self.global_data['market_cap_percentage']
        df = pd.DataFrame(data.items())
        df = df.rename(columns={0: 'symbol', 1: 'mktCap%'}).round(decimals=2)
        df.set_index('symbol', inplace=True)
        df = df.rename_axis(None)
        return df

    def total_market_cap(self):
        # extract the total market cap in trillion eur
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
        df_data_display = df_data_display.rename(columns={'market_cap_rank': 'mktCapRank'})
        df_data_display.set_index('symbol', inplace=True)
        df_data_display = df_data_display.rename_axis(None)
        return df_data_display


class EtherGasStats:
    # free API, private API key required, no call limit on website
    def __init__(self):
        self.url = 'https://ethgasstation.info/api/ethgasAPI.json?api-key=*INSERT API KEY HERE*'

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
        del data['gasPriceRange']
        stats = pd.DataFrame(data, index=[0])
        prices = stats.filter(['safeLow', 'average', 'fast', 'fastest'])
        # API values / 10 = Gwei
        prices.iloc[0] = prices.iloc[0] / 10
        times = stats.filter(
            ['safeLowWait', 'avgWait', 'fastWait', 'fastestWait']
        ).rename(columns={
            'safeLowWait': 'safeLow',
            'avgWait': 'average',
            'fastWait': 'fast',
            'fastestWait': 'fastest',
        })
        _blocks = stats.filter(['block_time', 'blockNum', 'speed'])
        _blocks.index = ['stats']
        _table = pd.concat([prices, times])
        _table.index = ['price (gwei)', 'time (min)']
        return _table, _blocks


class CurrencyConversion:
    # 5 requests / min. & 500 / day, private API key required
    def __init__(self):
        self.url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey=*INSERT API KEY HERE*'

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
        # define which currency you want to display the gas prices in (to_currency argument in url)
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
        # Whoops it wasn't a 200
        return "Error: " + str(e)

    # Must have been a 200 status code
    # json_obj = response.json()
    # return json_obj
