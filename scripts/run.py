from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress
from rich.progress import track
from rich.padding import Padding
from crypto_ticker import *
import time
import sys
import os

__VERSION__ = '2.2.1'

console = Console()
size = os.get_terminal_size()


class Tickerr:

    def __init__(self):
        # tables (type: DataFrame) to be generated for dashboard
        self.mkt_1 = None
        self.mkt_2 = None
        self.coin_stats = None
        self.trending = None
        self.gas_table = None
        self.gas_blocks = None

        # store time it took to update data
        update_time = float()

    def main(self):
        # print dashboard data tables
        console.rule('[bold red]Market stats')
        if size.columns > 118:
            console.print(f'Total market cap: T€ {self.mkt_1}\n'
                          f'Market cap change 24h: {self.mkt_2}')
        elif size.columns <= 118:
            console.print(Align(f'Total market cap: T€ {self.mkt_1}  |  '
                                f'{self.mkt_2} market cap change 24h',
                                align='center'))
        if size.lines > 30:
            console.rule(style='grey30')

        console.rule('[bold red]Coin Stats')
        # determine lines to print of coins table adjusted to terminal length
        # 19 lines
        # n_lines = self.size.lines - 19 if self.size.lines < 45 else 20
        if size.lines > 45:
            n_lines = 20
        elif size.lines < 45:
            n_lines = size.lines - 19
        elif size.lines < 20:
            n_lines = 1
        # self.console.print('n_lines =', n_lines)
        if size.lines <= 45:
            console.print(self.coin_stats.head(n_lines))
        elif size.lines > 45:
            console.print(self.coin_stats)
            console.rule(style='grey30')

        console.rule('[bold red]Trending')
        if size.lines <= 30:
            console.print(self.trending.head(3))
        elif size.lines > 30:
            console.print(self.trending)
            console.rule(style='grey30')

        console.rule('[bold red]Ether Gas Stats')
        console.print(f'{self.gas_table}')
        if size.lines > 30:
            console.print(f'\n{self.gas_blocks}')
        console.rule(style='grey30')

    def get_data(self, progress=False):
        time_start = time.time()
        if progress:
            total = 15  # steps
            # Initial call to print 0% progress
            printProgressBar(0, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        CGS = CoingeckoStats()
        if progress:
            printProgressBar(1, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        EGS = EtherGasStats()
        if progress:
            printProgressBar(2, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        #CCV = CurrencyConversion()  # suspended, no currency conversion needed in v2.2.1
        if progress:
            printProgressBar(3, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)

        # check API status
        # API calls have to be made to get data in some cases
        # printing the response is optional
        # console.rule('[grey]API status')
        response_cgs = check_api_status(CGS.api_call())
        if progress:
            printProgressBar(4, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        # console.print(f'CoinGecko: {CGS.api_call()}', style='grey42')
        response_egs = check_api_status(EGS.api_call())
        if progress:
            printProgressBar(5, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        # console.print(f'Eth Gas: {EGS.api_call()}', style='grey42')
        #response_ccv = check_api_status(CCV.api_call())
        if progress:
            printProgressBar(6, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        # print the error raised if any API response code != 200
        if not (response_cgs, response_egs):  # response_ccv suspended
            console.rule('[grey]API status')
            console.print('[Bold red] API status review:')
            console.print(f'CoinGecko API {response_cgs}')
            console.print(f'ETH Gas Station API {response_egs}')
            #console.print(f'Alpha Vantage API {response_ccv}')
            console.input('Please fix API connection/request.\nPress any key to exit...')
            sys.exit()
        # print(f'CurrencyLayer: {CC.api_call()}', style='grey42')
        # console.rule()

        # get data
        self.mkt_1 = CGS.total_market_cap()
        if progress:
            printProgressBar(7, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        self.mkt_2 = CGS.market_cap_change_percentage_24h_usd()
        if progress:
            printProgressBar(8, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)

        self.coin_stats = pd.concat([CGS.coins(), CGS.coins_11to20()])
        if progress:
            printProgressBar(9, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)

        # convert btc price in trending table to eur
        btc_price_eur = CGS.df_coin_prices_eur.iloc[0]['price (€)']
        if progress:
            printProgressBar(10, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        trending = CGS.trending()
        if progress:
            printProgressBar(11, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        trending = trending.sort_values(by='mktCapRank')
        if progress:
            printProgressBar(12, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        trending['price_btc'] = trending['price_btc'] * btc_price_eur
        if progress:
            printProgressBar(13, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        self.trending = trending.rename(columns={'price_btc': 'price (€)'}).round(decimals=6)
        if progress:
            printProgressBar(14, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)

        self.gas_table, self.gas_blocks = EGS.get_eth_gas_stats()
        if progress:
            printProgressBar(15, total, prefix='Updating:', suffix='Complete', length=50)
            time.sleep(0.1)
        time_end = time.time()
        self.update_time = time_end - time_start - 1.5


class Dashboard:
    def __init__(self):
        self.logo = self.set_logo()

    def header(self):
        console.clear()
        console.print(Panel(Align(self.logo, align='center'), style='yellow'))

    def footer(self, update_time = None):
        # self.cons.print(f'Updated at: {get_datetime()}', style='grey42', markup=False)
        # self.console.log('Data update', style='grey42')
        if size.lines > 30:
            console.print(f'[grey42]Version: {__version__}')
        if size.lines >= 27:
            console.print(f'\n[grey42]Updated at {datetime.now().strftime("%H:%M:%S")} | Duration: {update_time:.2f}s', end='')
        # self.console.print('Columns:', self.size.columns)
        # self.console.print('Lines', self.size.lines)

    def adder(self):
        # display 'ad'
        # adder() refreshes data while 'ad' is shown before entering next iteration
        self.header()
        '''
        with open('/home/pi/crypto_console/adder.txt', 'r') as f:
            adder = Panel(Padding(f.readlines(), 2))
        '''
        banner = r'''
 __   __     ______        ______     _____     ______
/\ "-.\ \   /\  __ \      /\  __ \   /\  __-.  /\  ___\
\ \ \-.  \  \ \ \/\ \     \ \  __ \  \ \ \/\ \ \ \___  \
 \ \_\\"\_\  \ \_____\     \ \_\ \_\  \ \____-  \/\_____\
  \/_/ \/_/   \/_____/      \/_/\/_/   \/____/   \/_____/

Made with fingers by 0x5042
'''
        adder = r'''
[bright_yellow]Want to make life even more exciting?[/bright_yellow]

[red]Go and get you some coins![/red]
[bright_black](Or tokens, I don't fucking care)[/bright_black]

A life-changing experience.
You will love it.
You hate to.


'''
        cup = '''
      ██    ██    ██
    ██      ██  ██
    ██    ██    ██
      ██  ██      ██
      ██    ██    ██
  ████████████████████
  ██                ██████
  ██                ██  ██
  ██                ██  ██
  ██                ██████
    ██            ██
████████████████████████
██                    ██
  ████████████████████
'''
        footer = '''
Made with sticky fingers by 0x504D42


'''

        console.print(Panel(Align(cup, align='center')))
        console.print(footer, justify='center')

    def set_logo(self):
        # if size < 81 columns, exit, terminal width not suffiecient
        if size.columns < 81:
            raise SizeError(f'Terminal width insufficient: Min. 81 columns, currently {size.columns} columns')
            # self.console.print('[bold red]SizeError[/bold red]: Terminal width insufficient (min. 81 columns)')
            # sys.exit(1)
        elif size.columns > 118:
            with open('cc_logo.txt', 'r', encoding='utf-8') as f:
                logo = f.read()
        elif size.columns <= 118:
            logo = f'Crypto Console {__version__}'
        return logo

    def network_check(self):
        while True:
            if not check_internet_connection():
                self.network_fail()
                continue
            break

    def network_fail(self):
        self.header()
        console.print('[bold red]InternetError[/bold red]: Internet connection not available.')
        self.update_time_progress()

    def update_time_progress(self):
        # progress bar to show time until next connection retry
        with Progress() as progress:
            task_update = progress.add_task('[cyan]Trying to reconnect...', total=30)
            while not progress.finished:
                progress.update(task_update, advance=1)
                time.sleep(1)

    def input_diag_shortcut(self):
        while True:
            usr_input = console.input('Enter "e" to exit or "r" to refresh: ')
            if usr_input == 'e':
                sys.exit()
            elif usr_input == 'r':
                return True
            else:
                continue


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    console.out(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


class SizeError(Exception):
    pass


def execution():
    CTR = Tickerr()
    DAS = Dashboard()
    first_run = True
    DAS.network_check()
    while True:
        DAS.header()
        if first_run:
            CTR.get_data()
            first_run = False
        CTR.main()
        DAS.footer(CTR.update_time)
        time.sleep(600)  # time between refreshes
        DAS.network_check()
        DAS.adder()
        CTR.get_data(progress=True)
        time.sleep(3)


if __name__ == '__main__':
    execution()
