### Insider_Monitor
An application built to pull insider activity from insider-monitor.com, stores it into PostgreSQL and CSV. Also enables user to use data visualization software such as tableau to see most significant trade(s)

You can find the website on www.willxiong.ca

### Example Pictures
![Example Image](https://github.com/willBear/Insider_Monitor/blob/master/Tableau%20Screen%20Shot.png)

### Getting Started
This application is built using Python 3.8.2 interpreter. See installation section and packages for list of requirements that are needed

You must install the packages that are contained in the requirements.txt file, simply navigate to the project root folder after it has been cloned/forked and run the following command 
```
pip install -r requirements.txt
```

### Deployment
To deploy this application, simply clone this repository and install packages that are contained in the requirements.txt file. 

Then, makesure your PostgreSQL is running, configure txt file to have the correct credentials 

Run init_database_postgre.py to have database tables built 

Run populate_10_day_data.py to have 10 days historial data stored into the database as well as exported to CSV

Ruu real_time_web_scraper to contain daily insider trade information 


## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
Thanks Mugel Geinberg for the Flask Mega Tutorial. Couldn't of done it without the support of you guys! <3 
