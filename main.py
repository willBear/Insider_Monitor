import requests
import csv
import datetime, time

# We store several API keys to make more API calls for free account, default is 12 per minute
alpha_vantage_api_keys = ["2MFOB84WZRAIGROV", "4NE2ALTFPGT83V3S"]
alpha_vantage_base_url = "https://www.alphavantage.co/query?function=OVERVIEW&symbol="

company_dict = []
failed_dict = []


def Retrieve_Company_Info(symbol, cik_number, count):
    alternate_index = count % 2
    company_url = alpha_vantage_base_url + symbol + "&apikey=" + alpha_vantage_api_keys[alternate_index]

    req_ob = requests.get(company_url)
    # result contains list of nested dictionaries
    result = req_ob.json()
    if len(result) > 1:
        company = result['Name']
        company = company.replace(",", "")
        exchange = result['Exchange']
        country = result['Country']
        sector = result['Sector']
        marketCap = result['MarketCapitalization']
        company_dict.append([company, symbol, exchange, country, sector, marketCap, cik_number])
        print("The new added company and its associate information is:" + str(company_dict[-1]))
    else:
        print("Failed loading ticker:" + symbol)
        failed_dict.append([symbol, cik_number])

    # Alpha Vantage Only Allows 5 API calls per minute
    time.sleep(7)

    return


def write_to_csv():
    file_name = "CIK_Company_" + str(datetime.date.today()) + '.csv'
    failed_file_name = "CIK_Failed_" + str(datetime.date.today()) + '.csv'
    company_fields = ['Company', 'Symbol', 'Exchange', 'Country', 'Sector', 'MarketCap', 'CIK_Number']
    failed_CIK_fields = ['Company', 'Symbol', 'Exchange', 'Country', 'Sector', 'MarketCap', 'CIK_Number']

    with open(file_name, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(company_fields)
        csvwriter.writerows(company_dict)
    print("Write to CSV Complete - The File name is: " + file_name)

    with open(failed_file_name,'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(failed_CIK_fields)
        csvwriter.writerows(failed_dict)
    print("Write to failed CSV Complete - The File name is: " + failed_file_name)
    return


def main():
    f = open("ticker.txt", "r")
    count = 0

    for line in f:
        cik_dict = line.split("	")
        symbol = cik_dict[0]
        cik_number = cik_dict[1][:-2]
        Retrieve_Company_Info(symbol, cik_number, count)
        print("The symbol is: " + str(cik_dict[0]) + " and the ticker is: " + str(cik_dict[1]))
        count += 1

    write_to_csv()


if __name__ == "__main__":
    main()
