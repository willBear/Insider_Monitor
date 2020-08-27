from bs4 import BeautifulSoup
from real_time_web_scraper import get_page_size, parse_row_info
import requests

insider_trades = []
trading_activity = {'B': 'Buy', 'S': 'Sell', 'O': 'Options Excersise'}


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
    base_url = 'https://www.insider-monitor.com/insiderbuy.php?days='
    index = 1
    while index < 10:
        url = base_url + str(index)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='html.parser')
        page_urls, length = find_pages_of_trades(soup.find_all("p", {"class": "linkp"}))

    soup = BeautifulSoup(response.text, features="html.parser")
    table_body = soup.find_all('tr')[1:]
    pass


if __name__ == "__main__":
    main()
    # 'https://www.insider-monitor.com/insiderbuy.php?days=1'
