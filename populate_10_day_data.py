from bs4 import BeautifulSoup
from datetime import datetime
import time
import requests

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
    now = datetime.utcnow()
    # Check to see if it contains symbol and company info, otherwise use previous
    if len(trades[-1]) == 0:
        return

    if len(trades[0]) > 1:
        symbol = trades[0]
        company = trades[1].split('  ')
        company = company[0]
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

    trade_shares, trade_price, trade_value = trades[3:6]

    trade_value = float(trade_value.replace(",", ""))
    trade_shares = float(trade_shares.replace(",", ""))
    trade_price = float(trade_price.replace(",", ""))

    trade_date = datetime.strptime(trades[6], '%Y-%m-%d')

    insider_trades.append(
        [symbol, company, insider, insider_position, trade_shares, trade_price, trade_value, trade_date, now])
    return


def find_pages_of_trades(soup_body):
    length = 0
    url_dict = []

    for row in soup_body:
        urls = row.find_all('a', href=True)
        for row in urls:
            next_page_url = row['href']
            if next_page_url in url_dict:
                pass
            else:
                url_dict.append(next_page_url)
            length += 1
    return url_dict, length


def main():
    base_buy_url = 'https://www.insider-monitor.com/insiderbuy.php?days='
    base_report_url = 'https://www.insider-monitor.com/reports/'
    index = 1
    while index < 10:
        # We navigate to the first day of insider buys
        url = base_buy_url + str(index)

        # Request to retrieve the first page
        response = requests.get(url)

        # Parse the text using bs4
        soup = BeautifulSoup(response.text, features='html.parser')

        # Retrieve the next page urls and length of pages in a particular day
        page_urls, total_pages = find_pages_of_trades(soup.find_all("p", {"class": "linkp"}))

        # Now we parse the current page of the report
        current_page = 1

        # Instantiate table body of the first page
        table_body = soup.find_all('tr')[1:]

        # While loop to traverse through number of pages
        while current_page <= total_pages:
            # Parse each row in table body
            for row in table_body:
                # Find all table entries
                trade = row.find_all('td')
                # Go through each row in table and strip the text
                row_info = [x.text.strip() for x in trade]
                # Parse the info from another python file
                parse_row_info(row_info)

            current_page += 1
            # Concatenate next url
            if len(page_urls) == 0:
                break
            else:
                next_page_url = base_report_url + page_urls[0]
                # Get rid of the next url
                page_urls.pop(0)
                response = requests.get(next_page_url)
                soup = BeautifulSoup(response.text, features='html.parser')
                table_body = soup.find_all('tr')[1:]
        index += 1

    soup = BeautifulSoup(response.text, features="html.parser")
    table_body = soup.find_all('tr')[1:]
    pass


if __name__ == "__main__":
    main()
    # 'https://www.insider-monitor.com/insiderbuy.php?days=1'
