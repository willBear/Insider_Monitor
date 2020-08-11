import requests
alpha_vantage_api_key = "2MFOB84WZRAIGROV"
alpha_vantage_base_url ="https://www.alphavantage.co/query?function=OVERVIEW&symbol="

def Retrieve_Company_Info(symbol):
    company_url = alpha_vantage_base_url +symbol+"&apikey=" + alpha_vantage_api_key

    req_ob = requests.get(company_url)

    # result contains list of nested dictionaries
    result = req_ob.json()
    print(result)
    return

def main():
    f = open("test.txt", "r")
    count = 0
    for line in f:
        cik_dict = line.split("	")
        symbol = cik_dict[0]
        Retrieve_Company_Info(symbol)
        print("The ticker is:" + str(cik_dict[0]) + " and the ticker is: " + str(cik_dict[1]))
        count += 1
if __name__ == "__main__":
    main()

