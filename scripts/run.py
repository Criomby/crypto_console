from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress
from crypto_ticker import *
import time
import sys


class Tickerr:

    def __init__(self):
        self.version = 'v1.0'
        self.console = Console()
        with open('cc_logo.txt', encoding='utf-8') as f:
            self.logo = f.read()

    def main(self):

        CGS = CoingeckoStats()
        EGS = EtherGasStats()
        CCV = CurrencyConversion()

        response_cgs = check_api_status(CGS.api_call())
        response_egs = check_api_status(EGS.api_call())
        response_ccv = check_api_status(CCV.api_call())
        if not (response_cgs, response_egs, response_ccv):
            self.console.rule('[grey]API status')
            self.console.print('[Bold red] API status review:')
            self.console.print(f'CoinGecko API {response_cgs}')
            self.console.print(f'ETH Gas.watch API {response_egs}')
            self.console.print(f'Alpha Vantage API {response_ccv}')
            self.console.input('Please fix API connection/request.\nPress any key to exit...')
            sys.exit()

        self.console.rule('[bold red]Market stats')
        self.console.print(f'''Total market cap: T€ {CGS.total_market_cap()}
Market cap change 24h: {CGS.market_cap_change_percentage_24h_usd()}''')
        self.console.rule(style='grey30')

        self.console.rule('[bold red]Coin Stats')
        self.console.print(pd.concat([CGS.coins(), CGS.coins_11to20()]))
        self.console.rule(style='grey30')

        self.console.rule('[bold red]Trending')
        btc_price_eur = CGS.df_coin_prices_eur.iloc[0]['price_€']
        trending = CGS.trending()
        trending = trending.sort_values(by='market_cap_rank')
        trending['price_btc'] = trending['price_btc'] * btc_price_eur
        trending = trending.rename(columns={'price_btc': 'price_€'}).round(decimals=6)
        self.console.print(trending)
        self.console.rule(style='grey30')

        self.console.rule('[bold red]Ether Gas Stats')
        gas_stats = EGS.get_eth_gas_stats()
        usd_eur_rate = CCV.get_fx_rate()
        gas_stats_eur = gas_stats.mul([1, usd_eur_rate], axis=0).round(decimals=2).rename(index={'usd': 'eur'})
        self.console.print(f'{gas_stats_eur}')
        self.console.rule(style='grey30')

    def input_diag_no_int(self):
        while True:
            usr_input = self.console.input('Enter "e" to exit or "t" to try again: ')
            if usr_input == 'e':
                sys.exit()
            elif usr_input == 't':
                return True
            else:
                continue

    def input_diag_shortcut(self):
        while True:
            usr_input = self.console.input('Enter "e" to exit or "r" to refresh: ')
            if usr_input == 'e':
                sys.exit()
            elif usr_input == 'r':
                return True
            else:
                continue

    def footer(self):
        self.console.log('Data update', style='grey42')
        self.console.print(f'Version: {self.version}', style='grey42')
        self.update_time_progress()

    def update_time_progress(self):
        with Progress() as progress:
            task_update = progress.add_task('[cyan]Waiting to update...', total=600)
            while not progress.finished:
                progress.update(task_update, advance=1)
                time.sleep(1)


if __name__ == '__main__':
    CTR = Tickerr()
    while True:
        try:
            while True:
                CTR.console.clear()
                CTR.console.print(Panel(Align(CTR.logo, align='center'), style='yellow'))
                if not check_internet_connection():
                    CTR.console.print('[bold red]-- No internet connection. --\nConnect to the internet and try again.\n')
                    if CTR.input_diag_no_int():
                        continue
                with CTR.console.status('Working...'):
                    CTR.main()
                CTR.footer()
        except KeyboardInterrupt:
            if CTR.input_diag_shortcut():
                continue
