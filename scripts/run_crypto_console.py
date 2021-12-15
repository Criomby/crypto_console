from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from crypto_ticker import *
import time
import sys

console = Console()


def main():

    CGS = CoingeckoStats()
    EGS = EtherGasStats()
    CCV = CurrencyConversion()

    response_cgs = check_api_status(CGS.api_call())
    response_egs = check_api_status(EGS.api_call())
    response_ccv = check_api_status(CCV.api_call())
    if not (response_cgs, response_egs, response_ccv):
        console.rule('[grey]API status')
        console.print('[Bold red] API status review:')
        console.print(f'CoinGecko API {response_cgs}')
        console.print(f'ETH Gas.watch API {response_egs}')
        console.print(f'Alpha Vantage API {response_ccv}')
        console.input('Please fix API connection/request.\nPress any key to exit...')
        sys.exit()

    console.rule('[bold red]Coin Stats')
    console.print(CGS.coins())
    console.rule()

    console.rule('[bold red]Market stats')
    console.print(f'''Total market cap: T€ {CGS.total_market_cap()}
Market cap change 24h: {CGS.market_cap_change_percentage_24h_usd()}\n''')

    btc_price_eur = CGS.df_coin_prices_eur.iloc[0]['price_€']
    trending = CGS.trending()
    trending = trending.sort_values(by='market_cap_rank')
    trending['price_btc'] = trending['price_btc'] * btc_price_eur
    trending = trending.rename(columns={'price_btc': 'price_€'}).round(decimals=2)
    console.print(f'Trending:', style='grey42')
    console.print(trending)
    console.rule()

    console.rule('[bold red]Ether Gas Stats')
    gas_stats = EGS.get_eth_gas_stats()
    usd_eur_rate = CCV.get_fx_rate()
    gas_stats_eur = gas_stats.mul([1, usd_eur_rate], axis=0).round(decimals=2).rename(index={'usd': 'eur'})
    console.print(f'{gas_stats_eur}')
    console.rule()

    console.print(f'Updated at: {get_datetime()}', style='grey42')


def input_diag_no_int():
    while True:
        usr_input = console.input('Enter "e" to exit or "t" to try again: ')
        if usr_input == 'e':
            sys.exit()
        elif usr_input == 't':
            return True
        else:
            continue


def input_diag_shortcut():
    while True:
        usr_input = console.input('Enter "e" to exit or "r" to refresh: ')
        if usr_input == 'e':
            sys.exit()
        elif usr_input == 'r':
            return True
        else:
            continue


if __name__ == '__main__':
    while True:
        try:
            while True:
                console.clear()
                console.print(Panel(Align('Crypto Console v1.1', align='center'), style='navajo_white1'))
                if not check_internet_connection():
                    console.print('[bold red]-- No internet connection. --\nConnect to the internet and try again.\n')
                    if input_diag_no_int():
                        continue
                with console.status('Working...'):
                    main()
                time.sleep(1800)
        except KeyboardInterrupt:
            if input_diag_shortcut():
                continue

# Copyright 2021 Philippe Braum
