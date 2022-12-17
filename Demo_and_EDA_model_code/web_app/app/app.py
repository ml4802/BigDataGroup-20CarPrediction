from flask import Flask, request, render_template
from tensorflow import keras as ks
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from bs4 import BeautifulSoup
import markupsafe
import requests

def get_img(year, make, model, color):

    url = "https://www.google.com/search?q={}+{}+{}+{}&tbm=isch&source".format(year, make, model, color)
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'lxml')
    image = soup.find("img", {"alt" : ""})
    
    return image['src']

if __name__ == '__main__':
    year = '2017'
    make = 'toyota'
    model = 'camry'

def scrapeAutoTrader(make, model, year, zipcode, city, state):
    url = "https://www.autotrader.com/cars-for-sale/all-cars/{}/{}/{}/{}-{}-{}?searchRadius=50&marketExtension=include&isNewSearch=true&showAccelerateBanner=false&sortBy=relevance&numRecords=100".format( \
        year, make, model, city, state, zipcode)

    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    results = soup.findAll("script", {"data-cmp" : "lstgSchema"})
    
    current_listings = []
    i = 0
    for item in results:
        i += 1
        text = item.get_text()
        index = text.find('"price":')
        secondIndex = text.find(',"priceValidUntil"')
        urlIndex = text.find('"url":')
        shortenedString = text[urlIndex+7:]
        shortenedSecondIndex = shortenedString.find("listingId")
        listingStingIndex = shortenedString[shortenedSecondIndex:].find('",')

        jump_url = shortenedString[:shortenedSecondIndex+listingStingIndex]
        if(text[index+8:secondIndex] == r"'0'" or text[index+8:secondIndex] == r'"0"'):
            continue 
        try:
            int(text[index+8:secondIndex])
        except:
            continue
        current_listings.append({"make": make, "model": model, "year": year, "price": int(text[index+8:secondIndex]), "url" : jump_url})

    return current_listings

def scrapeCars(make, model, year, zipcode):
    url = "https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]={}&maximum_distance=20&mileage_max=&models[]={}-{}&page=1&page_size=100&sort=best_match_desc&stock_type=all&year_max={}&year_min={}&zip={}".format( \
        make, make, model, year, year, zipcode)

    html_content = requests.get(url).text
    prefix = "https://www.cars.com"

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    results = soup.findAll("div", {"class" :"price-section price-section-vehicle-card"})
    scrapeUrl = soup.findAll("a", {"class" : "vehicle-card-link js-gallery-click-link"})
    
    current_listings = []
    for item in results:
        
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

    return current_listings

def one_hot(variable_to_find):
    columns = ['year', 'condition', 'cylinders', 'odometer', 'posting_date', 'income_this_year', 'manufactureracura', 'manufactureraudi', 'manufacturerbmw', 'manufacturerbuick', 'manufacturercadillac', 'manufacturerchevrolet', 'manufacturerchrysler', 'manufacturerdodge', 'manufacturerferrari', 'manufacturerford', 'manufacturergmc', 'manufacturerhonda', 'manufacturerhyundai', 'manufacturerjeep', 'manufacturerkia', 'manufacturerland.rover', 'manufacturerlexus', 'manufacturerlincoln', 'manufacturermazda', 'manufacturermercedes.benz', 'manufacturernissan', 'manufacturerother', 'manufacturerpontiac', 'manufacturerram', 'manufacturersubaru', 'manufacturertoyota', 'manufacturervolkswagen', 'fueldiesel', 'fuelelectric', 'fuelgas', 'fuelhybrid', 'fuelother', 'transmissionautomatic', 'transmissionmanual', 'transmissionother', 'drive4wd', 'drivefwd', 'driverwd', 'sizecompact', 'sizefull.size', 'sizemid.size', 'sizesub.compact', 'typeconvertible', 'typecoupe', 'typehatchback', 'typeother', 'typepickup', 'typesedan', 'typesuv', 'typetruck', 'typevan', 'paint_colorblack', 'paint_colorblue', 'paint_colorgrey', 'paint_colorother', 'paint_colorred', 'paint_colorsilver', 'paint_colorwhite']
    for i in range(len(columns)):
        if variable_to_find.lower() in columns[i]:
            return i
    return -1

def test_get_info(query):
    columns = ['year', 'condition', 'cylinders', 'odometer', 'posting_date', 'income_this_year', 'manufactureracura', 'manufactureraudi', 'manufacturerbmw', 'manufacturerbuick', 'manufacturercadillac', 'manufacturerchevrolet', 'manufacturerchrysler', 'manufacturerdodge', 'manufacturerferrari', 'manufacturerford', 'manufacturergmc', 'manufacturerhonda', 'manufacturerhyundai', 'manufacturerjeep', 'manufacturerkia', 'manufacturerland.rover', 'manufacturerlexus', 'manufacturerlincoln', 'manufacturermazda', 'manufacturermercedes.benz', 'manufacturernissan', 'manufacturerother', 'manufacturerpontiac', 'manufacturerram', 'manufacturersubaru', 'manufacturertoyota', 'manufacturervolkswagen', 'fueldiesel', 'fuelelectric', 'fuelgas', 'fuelhybrid', 'fuelother', 'transmissionautomatic', 'transmissionmanual', 'transmissionother', 'drive4wd', 'drivefwd', 'driverwd', 'sizecompact', 'sizefull.size', 'sizemid.size', 'sizesub.compact', 'typeconvertible', 'typecoupe', 'typehatchback', 'typeother', 'typepickup', 'typesedan', 'typesuv', 'typetruck', 'typevan', 'paint_colorblack', 'paint_colorblue', 'paint_colorgrey', 'paint_colorother', 'paint_colorred', 'paint_colorsilver', 'paint_colorwhite']
    for i in range(64):
        print(columns[i], query[0,i])

def get_similar_models(model, size, year, type, cylinders, EDA_data):

    similar = EDA_data[EDA_data['model'] == model.lower()]
    similar = similar[similar['price'] != "0.0"]
    similar = similar.drop_duplicates()
    similar = similar[similar['year'] == year]
    similar = similar.drop(columns=['income_this_year', 'posting_date', 'cylinders'])
    similar.insert(0, 'state', similar.pop('state'))
    return similar

app = Flask(__name__)

EDA_data = pd.read_csv('BigDataGroup-20CarPrediction/Demo_and_EDA_model_code/with_income.csv')

one_hot_data = pd.read_csv('BigDataGroup-20CarPrediction/Demo_and_EDA_model_code/one_hotted_training_data.csv')
one_hot_data = one_hot_data[one_hot_data['price'] <= 50000]
one_hot_data = one_hot_data[one_hot_data['price'] > 1000]
#print(one_hot_data.price.describe())
#one_hot_data

train, test = train_test_split(one_hot_data, test_size=0.2)
X_train = train.drop('price', axis=1).to_numpy()
y_train = train['price'].to_numpy()
X_valid = test.drop('price', axis=1).to_numpy()
y_valid = test['price'].to_numpy()

model_Tree = DecisionTreeClassifier()
model_Tree = model_Tree.fit(X_train,y_train)

# Loading models in
model_NN = ks.models.load_model('BigDataGroup-20CarPrediction/Demo_and_EDA_model_code/web_app/app/Overall.h5')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 65 columns (including price)
        query = np.zeros([1,64])

        Model = request.form.get('Model')
        print(Model)

        Manufacturer = request.form.get('Manufacturer')
        query[0,one_hot(Manufacturer)] = 1

        Year = int(request.form.get('Year'))
        query[0,one_hot("year")] = Year

        Miles = int(request.form.get('miles'))
        query[0,one_hot("odometer")] = Miles

        PostingDate = 2021
        query[0,one_hot("posting_date")] = PostingDate

        income_this_year = int(request.form.get('State_income')) # Change this to average income per state later
        query[0,one_hot("income_this_year")] = income_this_year

        Fuel = request.form.get('Fuel')
        query[0,one_hot(Fuel)] = 1

        Condition = request.form.get('Condition')
        query[0,one_hot('condition')] = Condition

        Cylinders = request.form.get('Cylinders')
        query[0,one_hot('cylinders')] = Cylinders

        Transmission = request.form.get('Transmission')
        query[0,one_hot(Transmission)] = 1
        
        Drive = request.form.get('Drive')
        query[0,one_hot(Drive)] = 1

        Size = request.form.get('Size')
        query[0,one_hot(Size)] = 1

        Type = request.form.get('Type')
        query[0,one_hot(Type)] = 1

        Paint = request.form.get('Paint')
        query[0,one_hot("color"+Paint)] = 1

        Seller_Type_Individual = request.form.get('Seller_Type_Individual')

        Zipcode = request.form.get('Zipcode')
        print(Zipcode)

        similar_models = get_similar_models(Model, Size, Year, Type, Cylinders, EDA_data)
        # NN Prediction
        pred_NN = model_NN.predict(query)[0,0]
        pred_Tree = model_Tree.predict(query)[0]
        preds_all = [{"pred_Tree" :pred_Tree, "pred_NN":pred_NN}]

        # Doing multiple model graphs
        list_of_NN_preds = {}
        list_of_Tree_preds = {}
        list_of_years = {}
        t = 0
        for i in range(Year-2, Year+3):
            query[0,one_hot("year")] = i
            list_of_NN_preds[str(t)] = model_NN.predict(query)[0,0]
            list_of_Tree_preds[str(t)] = model_Tree.predict(query)[0]
            list_of_years[str(t)] = str(i)
            t+=1

        autotrader = scrapeAutoTrader(str(Manufacturer), str(Model), str(int(Year)), str(int(Zipcode)), "PLACEHOLDER", "PLACEHOLDER")
        cars = scrapeCars(str(Manufacturer), str(Model), str(int(Year)), str(int(Zipcode)))
        
        autotrader  = pd.DataFrame.from_dict(autotrader)
        cars  = pd.DataFrame.from_dict(cars)
        imageurl = str(get_img(year, Manufacturer, Model, Paint))
        print(imageurl)

        lowest = str(list_of_Tree_preds[min(list_of_Tree_preds, key=list_of_Tree_preds.get)])
        highest =  str(list_of_Tree_preds[max(list_of_Tree_preds, key=list_of_Tree_preds.get)])
        #imageurl = "https://production-media.paperswithcode.com/datasets/VehicleX-0000005478-67034544.jpg"
        #return render_template('resultpage.html', data=preds_all, tables = [similar_models.to_html()], autotrader=[autotrader.to_html()], cars=[cars.to_html()], image=imageurl, zip=str(Zipcode), manufacturer=str(Manufacturer), model=str(Model),color=str(Paint), year=str(Year), list_of_NN_preds=list_of_NN_preds, list_of_Tree_preds=list_of_Tree_preds)
        return render_template('resultpage.html', lowest = lowest, highest=highest,car0=list_of_Tree_preds['0'], car1=list_of_Tree_preds['1'],car2=list_of_Tree_preds['2'],car3=list_of_Tree_preds['3'],car4=list_of_Tree_preds['4'], year0 = list_of_years['0'],year1 = list_of_years['1'],year2 = list_of_years['2'],year3 = list_of_years['3'],year4 = list_of_years['4'], data=preds_all, tables = [similar_models.to_html()], autotrader=[autotrader.to_html()], cars=[cars.to_html()], image=imageurl, zip=str(Zipcode), manufacturer=str(Manufacturer), model=str(Model),color=str(Paint), year=str(Year))
    return render_template('querypage.html')

if __name__ == '__main__':
    app.run(debug=True)