####################################################
#                                                  #
# Author(s): Car Price Prediction Group - Zachary  #
#            Burpee, Ming Liu, Napasorn Phongphaew #
# Class: Big Data Analytics Final Project          #
# Professor: Professor Ching-Yung Lin              #
# Description: Webscraping tool to scrape the      #
#              current listings of AutoTader.com   #
#              and Cars.com and returns current    #
#              results                             #
#                                                  #
####################################################

from bs4 import BeautifulSoup
import requests

def scrapeAutoTrader(make, model, year, zipcode, city, state):
    '''
    Description: Funtion designed to query AutoTrader.com specifically by taking inputs of a 
        specific car make, model, year, and zipcode to plug into the different filters of 
        AutoTrader. The search radius is natively 50 miles and the first 100 results are returned
    Inputs: 
        - Make (string): Car make, lowercase, has to be a valid make on AutoTrader.com
        - Model (string): Car model, lowercase, has to be a valid model of a car make on AutoTrader.com
        - Year (string): Car year, number format "2022", of a valid car year for make/model
        - Zipcode (string): Zipcode search, number format, of a valid zipcode in the U.S. 
        - City (string): City search, has to be valid city that corresponds to zipcode in U.S.
        - State (string): State search, lowercase, has to be valid state that corresponds to state in U.S. 
    Outputs:
        - Current_listings (dictionary): Dictionary/Map of current listings (sorted by most relevant results) 
            including make, model, year, price, and current URL to listing
    '''

    # Create custom URL to send to browser
    url = "https://www.autotrader.com/cars-for-sale/all-cars/{}/{}/{}/{}-{}-{}?searchRadius=50&marketExtension=include&isNewSearch=true&showAccelerateBanner=false&sortBy=relevance&numRecords=100".format( \
        year, make, model, city, state, zipcode)

    # Get HTML elements in text format
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    # Return list of static "listing XPATH" results 
    results = soup.findAll("script", {"data-cmp" : "lstgSchema"})
    
    # Parse listings in results and create dictionary of first 100 listings
    current_listings = []
    i = 0
    for item in results:
        i += 1
        # Turn elemnts into text values and extract featurs of price and listing URL
        text = item.get_text()
        index = text.find('"price":')
        secondIndex = text.find(',"priceValidUntil"')
        urlIndex = text.find('"url":')
        shortenedString = text[urlIndex+7:]
        shortenedSecondIndex = shortenedString.find("listingId")
        listingStingIndex = shortenedString[shortenedSecondIndex:].find('",')
        jump_url = shortenedString[:shortenedSecondIndex+listingStingIndex]

        # Append listing to dictionary
        try:
            current_listings.append({"make": make, "model": model, "year": year, "price": int(text[index+8:secondIndex]), "url" : jump_url})
        except:
            continue
    # Return dictionary
    return current_listings

def scrapeCars(make, model, year, zipcode):
    '''
    Description: Funtion designed to query Cars.com specifically by taking inputs of a 
        specific car make, model, year, and zipcode to plug into the different filters of 
        Cars.com. The search radius is natively 50 miles and the first 100 results are returned
    Inputs: 
        - Make (string): Car make, lowercase, has to be a valid make on Cars.com
        - Model (string): Car model, lowercase, has to be a valid model of a car make on Cars.com
        - Year (string): Car year, number format "2022", of a valid car year for make/model
        - Zipcode (string): Zipcode search, number format, of a valid zipcode in the U.S. 
        - City (string): City search, has to be valid city that corresponds to zipcode in U.S.
        - State (string): State search, lowercase, has to be valid state that corresponds to state in U.S. 
    Outputs:
        - Current_listings (dictionary): Dictionary/Map of current listings (sorted by most relevant results) 
            including make, model, year, price, and current URL to listing
    '''

    # Create custom URL to send to browser
    url = "https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]={}&maximum_distance=20&mileage_max=&models[]={}-{}&page=1&page_size=100&sort=best_match_desc&stock_type=all&year_max={}&year_min={}&zip={}".format( \
        make, make, model, year, year, zipcode)

    # Get HTML elements in text format
    html_content = requests.get(url).text
    prefix = "https://www.cars.com"

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    # Return list of static "listing XPATH" results 
    results = soup.findAll("div", {"class" :"price-section price-section-vehicle-card"})
    # Return list of static "URL XPATH" results for each listing 
    scrapeUrl = soup.findAll("a", {"class" : "vehicle-card-link js-gallery-click-link"})
        
    # Parse listings in results and create dictionary of first 100 listings
    current_listings = []
    for item in results:
        # Loop to find all prices extracted
        text = item.get_text()
        # eliminate any price drops
        text = text.strip().split()[0]
        temp = ""
        for element in text:
            if element.isnumeric():
                temp += element
        try:
            int(temp)
        except:
            continue
        current_listings.append({"make": make, "model": model, "year": year, "price": int(temp)})

    i = 0
    for text in scrapeUrl:
        # Loop to find all URLs that correspond to listings 
        text = str(text).strip()
        index = text.find(' href="')
        secondIndex = text.find('" rel="nofollow"')
        jump_url = text[index+7:secondIndex]
        print(i)
        try:
            current_listings[i]["url"] = prefix + jump_url
        except:
            continue
        i+= 1

    # Return current listings 
    return current_listings


if __name__=="__main__":
    # Test values to see what is returned (eliminated in function calls)
    make = "toyota"
    model = "corolla"
    year = '2019'
    zipcode = '95124'
    state = 'ca' 
    city = 'san-jose'

    print(scrapeAutoTrader(make, model, year, zipcode, city, state))
    print(scrapeCars(make, model, year, zipcode))








