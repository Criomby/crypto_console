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
            # uncomment this line and define names to get desired coins e.g.:
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
            df_data = df_data.append(df)

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
        try:
            data = json.loads(self.response.text)
            stats = pd.DataFrame(data, columns=['slow', 'normal', 'fast', 'instant'])
            return stats
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return e


class CurrencyConversion:
    def __init__(self):
        self.url = 'http://api.currencylayer.com/live?access_key=* your key here *'

        headers = {
            'Accepts': 'application/json',
        }

        self.session = Session()
        self.session.headers.update(headers)
        self.response = dict()
        self.rate_usd_eur = float()

    def api_call(self):
        try:
            self.response = self.session.get(self.url)
            return self.response
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return e

    def get_rate(self):
        # data = json.loads(self.response.text)

        # testing data (equivalent to the real api data)
        data = {'success': True, 'terms': 'https://currencylayer.com/terms',
                'privacy': 'https://currencylayer.com/privacy', 'timestamp': 1638864604, 'source': 'USD',
                'quotes': {'USDAED': 3.673045, 'USDAFN': 96.170039, 'USDALL': 107.148713, 'USDAMD': 491.708104,
                           'USDANG': 1.80388, 'USDAOA': 564.209024, 'USDARS': 101.2478, 'USDAUD': 1.409592,
                           'USDAWG': 1.8, 'USDAZN': 1.688272, 'USDBAM': 1.733531, 'USDBBD': 2.020944,
                           'USDBDT': 85.872927, 'USDBGN': 1.732065, 'USDBHD': 0.376996, 'USDBIF': 1994.3451,
                           'USDBMD': 1, 'USDBND': 1.370312, 'USDBOB': 6.911326, 'USDBRL': 5.689703, 'USDBSD': 1.000944,
                           'USDBTC': 1.9607589e-05, 'USDBTN': 75.39279, 'USDBWP': 11.747907, 'USDBYN': 2.549203,
                           'USDBYR': 19600, 'USDBZD': 2.017576, 'USDCAD': 1.272435, 'USDCDF': 2004.000119,
                           'USDCHF': 0.924215, 'USDCLF': 0.030665, 'USDCLP': 846.130261, 'USDCNY': 6.3684,
                           'USDCOP': 3932.5, 'USDCRC': 630.010592, 'USDCUC': 1, 'USDCUP': 26.5, 'USDCVE': 97.734464,
                           'USDCZK': 22.515978, 'USDDJF': 178.189827, 'USDDKK': 6.588405, 'USDDOP': 56.811746,
                           'USDDZD': 139.22503, 'USDEGP': 15.744101, 'USDERN': 15.00031, 'USDETB': 48.619038,
                           'USDEUR': 0.885995, 'USDFJD': 2.14275, 'USDFKP': 0.745434, 'USDGBP': 0.753005,
                           'USDGEL': 3.10499, 'USDGGP': 0.745434, 'USDGHS': 6.180764, 'USDGIP': 0.745434,
                           'USDGMD': 52.55548, 'USDGNF': 9512.945285, 'USDGTQ': 7.750242, 'USDGYD': 209.307376,
                           'USDHKD': 7.79952, 'USDHNL': 24.17936, 'USDHRK': 6.665901, 'USDHTG': 100.66875,
                           'USDHUF': 323.280162, 'USDIDR': 14381.25, 'USDILS': 3.15785, 'USDIMP': 0.745434,
                           'USDINR': 75.418003, 'USDIQD': 1460.340533, 'USDIRR': 42274.999981, 'USDISK': 130.405939,
                           'USDJEP': 0.745434, 'USDJMD': 155.292116, 'USDJOD': 0.709199, 'USDJPY': 113.722977,
                           'USDKES': 112.749978, 'USDKGS': 84.794203, 'USDKHR': 4077.732722, 'USDKMF': 436.250123,
                           'USDKPW': 900.00035, 'USDKRW': 1177.379703, 'USDKWD': 0.30273, 'USDKYD': 0.834138,
                           'USDKZT': 438.855553, 'USDLAK': 10904.070978, 'USDLBP': 1513.425838, 'USDLKR': 202.936901,
                           'USDLRD': 142.000237, 'USDLSL': 16.110204, 'USDLTL': 2.95274, 'USDLVL': 0.60489,
                           'USDLYD': 4.601346, 'USDMAD': 9.21519, 'USDMDL': 17.676037, 'USDMGA': 3983.655887,
                           'USDMKD': 54.591758, 'USDMMK': 1781.633082, 'USDMNT': 2858.218612, 'USDMOP': 8.042686,
                           'USDMRO': 356.999828, 'USDMUR': 44.000468, 'USDMVR': 15.450038, 'USDMWK': 817.704645,
                           'USDMXN': 21.20179, 'USDMYR': 4.228029, 'USDMZN': 63.830125, 'USDNAD': 16.109797,
                           'USDNGN': 409.989657, 'USDNIO': 35.26247, 'USDNOK': 9.050202, 'USDNPR': 120.625579,
                           'USDNZD': 1.477675, 'USDOMR': 0.385048, 'USDPAB': 1.000944, 'USDPEN': 4.086435,
                           'USDPGK': 3.559532, 'USDPHP': 50.338504, 'USDPKR': 176.664303, 'USDPLN': 4.070988,
                           'USDPYG': 6805.67435, 'USDQAR': 3.641018, 'USDRON': 4.382802, 'USDRSD': 104.150384,
                           'USDRUB': 74.17897, 'USDRWF': 1037.106631, 'USDSAR': 3.751178, 'USDSBD': 8.067802,
                           'USDSCR': 13.549293, 'USDSDG': 437.505044, 'USDSEK': 9.068781, 'USDSGD': 1.366225,
                           'USDSHP': 1.377396, 'USDSLL': 11140.000394, 'USDSOS': 586.000165, 'USDSRD': 21.533023,
                           'USDSTD': 20697.981008, 'USDSVC': 8.757966, 'USDSYP': 1256.783558, 'USDSZL': 15.970822,
                           'USDTHB': 33.68601, 'USDTJS': 11.305608, 'USDTMT': 3.5, 'USDTND': 2.887495,
                           'USDTOP': 2.29445, 'USDTRY': 13.753145, 'USDTTD': 6.803489, 'USDTWD': 27.759501,
                           'USDTZS': 2303.000168, 'USDUAH': 27.401649, 'USDUGX': 3573.248718, 'USDUSD': 1,
                           'USDUYU': 44.211627, 'USDUZS': 10779.660266, 'USDVEF': 213830222338.07285, 'USDVND': 23110,
                           'USDVUV': 111.319609, 'USDWST': 2.563641, 'USDXAF': 581.401038, 'USDXAG': 0.044566,
                           'USDXAU': 0.000561, 'USDXCD': 2.70255, 'USDXDR': 0.715631, 'USDXOF': 581.401038,
                           'USDXPF': 106.298393, 'USDYER': 250.250037, 'USDZAR': 15.89181, 'USDZMK': 9001.202932,
                           'USDZMW': 17.641183, 'USDZWL': 321.999592}}

        # define which currency you want to display the gas prices in (USD to XXX: 'USDXXX')
        usd_eur_rate = data['quotes']['USDEUR']
        return usd_eur_rate


def get_update_time():
    now = datetime.now()
    return now.strftime("%d.%m.%Y %H:%M:%S")
