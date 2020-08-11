import requests
import csv
import time
alpha_vantage_api_key = "2MFOB84WZRAIGROV"
alpha_vantage_base_url ="https://www.alphavantage.co/query?function=OVERVIEW&symbol="
company_dict =[]
def Retrieve_Company_Info(symbol,count):

    company_url = alpha_vantage_base_url + symbol + "&apikey=" + alpha_vantage_api_key
    req_ob = requests.get(company_url)
    # result contains list of nested dictionaries
    result = req_ob.json()
    if len(result) > 0:
        company = result['Name']
        exchange = result['Exchange']
        country = result['Country']
        sector = result['Sector']
        marketCap = result['MarketCapitalization']
        company_dict.append([company, exchange, country, sector, marketCap])
        print(str(company_dict[:-1]))

        # Alpha Vantage Only Allows 5 API calls per minute
        time.sleep(12)
    else:
        print("Failed loading ticker:" + symbol)


    return

def main():
    f = open("test.txt", "r")
    count = 0
    for line in f:
        cik_dict = line.split("	")
        symbol = cik_dict[0]
        Retrieve_Company_Info(symbol,count)
        print("The ticker is:" + str(cik_dict[0]) + " and the ticker is: " + str(cik_dict[1]))
        count += 1
if __name__ == "__main__":
    main()

