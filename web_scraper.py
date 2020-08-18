from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
import requests
from init_database_postgre import load_db_credential_info

insider_trades = []
trading_activity = {'B': 'Buy', 'S': 'Sell', 'O': 'Options Excersise'}
base_url = 'https://www.insider-monitor.com/insider_stock_trading_report.html'


def parse_row_info(trades):
    """
    :param trades:
    Contains usually 7 indexes, which are:
    Ticker, Company Information, Person Filling & Position, Buy/Sell or Options Excersize, Share and Price,
    Value, Trade Date & Time
    :return:
    """
    now = datetime.utcnow()
    # Check to see if it contains symbol and company info, otherwise use previous
    test = len(trades[-1])
    if len(trades[-1]) == 0:
        return

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
    trade_shares = float(trade_shares.replace(",", ""))
    trade_price = float(trade_price.replace(",", ""))

    trade_date = datetime.strptime(trades[6], '%Y-%m-%d%H:%M:%S')

    insider_trades.append(
        [symbol, company, insider, insider_position, trade_type, trade_shares, trade_price, trade_date,now])
    return


def get_page_size(h1_content):
    """
    :param h1_content: determine the total number of pages we have to scrape for
    :return: the number of pages that are contained in the report
    """

    # Iterate through each row and find 'page'
    for row in h1_content:
        # If contains pages, we assume its greater than 1 page
        if 'page' in row:
            info = row.text
            page_size = info[-2]
            return int(page_size)
        # Otherwise, we would only parse the first page
        else:
            return 1

def update_insider_trades(db_host, db_user, db_password, db_name):
    # Connect to our PostgreSQL database
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)

    column_str = ('symbol,company,insider_name,insider_position,insider_order_type,trade_shares_quantity,trade_shares_price,reported_date,created_date')
    insert_str = ("%s," * 9)[:-1]
    final_str = "INSERT INTO insider_trades (%s) VALUES (%s)" % (column_str, insert_str)
    with conn:
        cur = conn.cursor()
        cur.executemany(final_str, insider_trades)

def main():
    now = datetime.utcnow()

    response = requests.get("https://www.insider-monitor.com/insider_stock_trading_report.html")

    soup = BeautifulSoup(response.text, features="html.parser")

    table_body = soup.find_all('tr')[1:]
    header = soup.find('h1')
    page_size = get_page_size(header)

    for row in table_body:
        trade = row.find_all('td')
        row_info = [x.text.strip() for x in trade]
        parse_row_info(row_info)

    # name of our database credential files (.txt)
    db_credential_info = "database_info.txt"

    # create a path version of our text file
    db_credential_info_p = '/' + db_credential_info

    # create our instance variables for host, username, password and database name
    db_host, db_user, db_password, db_name = load_db_credential_info(db_credential_info_p)

    update_insider_trades(db_host, db_user, db_password, db_name)

if __name__ == "__main__":
    main()
