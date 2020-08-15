import datetime
from bs4 import BeautifulSoup
import psycopg2
import requests
import os

def main():
    now = datetime.datetime.utcnow()

    response = requests.get("https://www.insider-monitor.com/insider_stock_trading_report.html")

    soup = BeautifulSoup(response.text, features="html.parser")

    table_body = soup.find_all('tr')[1:]
    for row in table_body:
        trade = row.find_all('td')
        row_info = [x.text.strip() for x in trade]
        pass
    pass


if __name__ == "__main__":
    main()