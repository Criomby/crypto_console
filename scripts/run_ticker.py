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
    CC = CurrencyConversion()

    # printing the API response is optional
    # console.rule('[grey]API status')
    CGS.api_call()
    # console.print(f'CoinGecko: {CGS.api_call()}', style='grey42')
    EGS.api_call()
    # console.print(f'Eth Gas: {EGS.api_call()}', style='grey42')
    # print(f'CurrencyLayer: {CC.api_call()}', style='grey42')
    # console.rule()

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
    usd_eur_rate = CC.get_rate()
    gas_stats_eur = gas_stats.mul([1, usd_eur_rate], axis=0).round(decimals=2).rename(index={'usd': 'eur'})
    console.print(f'{gas_stats_eur}')
    console.rule()

    console.print(f'Updated at: {get_update_time()}', style='grey42')


if __name__ == '__main__':
    try:
        while True:
            console.clear()
            console.print(Panel(Align('Crypto Console v1.0', align='center'), style='navajo_white1'))
            with console.status('Working...'):
                main()
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
