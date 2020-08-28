from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
import requests
import schedule
import time
import csv
from os import path
from init_database_postgre import load_db_credential_info

insider_trades = []
trading_activity = {'B': 'Buy', 'S': 'Sell', 'O': 'Options Excersise'}
base_url = 'https://www.insider-monitor.com/insider_stock_trading_report'


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
        # insider, insider_position = trades[2].split("(")
        info = trades[2].split("(")
        if len(info) > 2:
            insider = info[0:-2]
            insider_position = info[-1]
            insider = insider[0].strip()
        else:
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
        [symbol, company, insider, insider_position, trade_type, trade_shares, trade_price, trade_date, now])
    return


def get_page_size(h1_content):
    """
    :param h1_content: determine the total number of pages we have to scrape for
    :return: the number of pages that are contained in the report
    """
    # Iterate through each row and find 'page'
    for row in h1_content:
        # If contains pages, we assume its greater than 1 page
        content = row.text
        if 'page' in content:
            info = row.text
            page_size = info[-2]
            return int(page_size)
            pass
        # Otherwise, we would only parse the first page
        else:
            return 1


def update_insider_trades(db_host, db_user, db_password, db_name, insider_trade_dict):
    # Connect to our PostgreSQL database
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)

    column_str = (
        'symbol,company,insider_name,insider_position,insider_order_type,trade_shares_quantity,trade_shares_price,'
        'trade_value,reported_date,created_date')
    insert_str = ("%s," * 10)[:-1]
    final_str = "INSERT INTO insider_trades (%s) VALUES (%s)" % (column_str, insert_str)
    with conn:
        cur = conn.cursor()
        cur.executemany(final_str, insider_trade_dict)
    print("Insert into DB Completed, with " + str(len(insider_trade_dict)) + " entries")


def write_to_csv(insider_trades_dict):
    insider_trade_fields = ["symbol", "company", "insider", "insider_position", "trade_type", "trade_shares",
                            "trade_price","trade_value",
                            "trade_date", "now"]
    file_name = 'Insider_Trades.csv'
    # Check for existence of CSV file
    if path.exists(file_name):
        print('Existing file is found, appending to last row')
        with open(file_name, 'a+') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(insider_trades)
    else:
        print("CSV File is not found, making a new file ")
        with open(file_name, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(insider_trade_fields)
            csvwriter.writerows(insider_trades_dict)
    print("Write to CSV Complete - The File name is: " + file_name)

    return


def main():
    response = requests.get("https://www.insider-monitor.com/insider_stock_trading_report.html")
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    soup = BeautifulSoup(response.text, features="html.parser")

    table_body = soup.find_all('tr')[1:]
    header = soup.find('h1')
    page_size = get_page_size(header)
    current_page = 1
    while current_page <= page_size:
        for row in table_body:
            trade = row.find_all('td')
            row_info = [x.text.strip() for x in trade]
            parse_row_info(row_info)
        current_page += 1
        current_page_url = base_url + '-' + str(current_page) + '.html'
        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.text, features="html.parser")
        table_body = soup.find_all('tr')[1:]
        pass

    # name of our database credential files (.txt)
    db_credential_info = "database_info.txt"

    # create a path version of our text file
    db_credential_info_p = '/' + db_credential_info

    # create our instance variables for host, username, password and database name
    db_host, db_user, db_password, db_name = load_db_credential_info(db_credential_info_p)

    update_insider_trades(db_host, db_user, db_password, db_name)

    write_to_csv()

    print('The Time is: ' + date_time + ' Parsed ' + str(page_size) + ' pages of insider trades')


def scheduler():
    schedule.every().day.at("11:55").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # scheduler()
    main()
