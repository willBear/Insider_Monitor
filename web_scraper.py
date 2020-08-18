from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
import requests
import os

insider_trades = []
trading_activity = {'B': 'Buy', 'S': 'Sell', 'O': 'Options Excersise'}
def parse_row_info(trades):
    """
    :param trades:
    Contains usually 7 indexes, which are:
    Ticker, Company Information, Person Filling & Position, Buy/Sell or Options Excersize, Share and Price,
    Value, Trade Date & Time
    :return:
    """
    # Check to see if it contains symbol and company info, otherwise use previous
    if len(trades[0]) > 1:
        symbol = trades[0]
        company = trades[1].split('(' + symbol + ')')[0]
        company = company.strip()
    else:
        last_trade = insider_trades[-1]
        symbol = last_trade[0]
        company = last_trade[1]

    if '(' in trades[2]:
        insider, insider_position = trades[2].split("(")
    else:
        insider = trades[2]
        insider_position = ''

    insider = insider.strip()
    insider_position = insider_position[:-1]

    trade_type = trading_activity[trades[3]]

    trade_shares, trade_price = trades[4].split(" $")
    trade_shares = float(trade_shares.replace(",",""))
    trade_price = float(trade_price.replace(",",""))

    trade_date = datetime.strptime(trades[6],'%Y-%m-%d%H:%M:%S')

    insider_trades.append(
        [symbol, company, insider, insider_position, trade_type, trade_shares, trade_price, trade_date])
    return


def main():
    now = datetime.utcnow()

    response = requests.get("https://www.insider-monitor.com/insider_stock_trading_report.html")

    soup = BeautifulSoup(response.text, features="html.parser")

    table_body = soup.find_all('tr')[1:]
    for row in table_body:
        trade = row.find_all('td')
        row_info = [x.text.strip() for x in trade]
        parse_row_info(row_info)

if __name__ == "__main__":
    main()
