from __future__ import print_function

import datetime
import bs4
import psycopg2
import requests
import os

def main():
    now = datetime.datetime.utcnow()

    response = requests.get("https://www.insider-monitor.com/insider_stock_trading_report.html")

    soup = bs4.BeautifulSoup(response.text)

    insider_trades = soup.find_all('tr')


    pass


if __name__ == "__main__":
    main()