####################################################
#                                                  #
# Author(s): Car Price Prediction Group - Zachary  #
#            Burpee, Ming Liu, Napasorn Phongphaew #
# Class: Big Data Analytics Final Project          #
# Professor: Professor Ching-Yung Lin              #
# Description: Main application for running        #
#              flask webserver, run this and then  #
#              navigate to http://127.0.0.1:5000   #
#              Requires Tensorflow to be installed #                 
#                                                  #
####################################################

from flask import Flask, request, render_template
from tensorflow import keras as ks
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from scraper import scrapeAutoTrader
from scraper import scrapeCars
from imageSearch import get_google_img

if __name__ == '__main__':
    print("start")

def one_hot(variable_to_find):
    """
        Description: Retrives the index of a given column in the query entry, 
        for later one-hotting
    Inputs: 
        - variable_to_find (string): "Model" etc to find the index of "Model" 
    Outputs:
        - i: returns the correct column index for the query
    """
    columns = ['year', 'condition', 'cylinders', 'odometer', 'posting_date', 'income_this_year', 'manufactureracura', 'manufactureraudi', 'manufacturerbmw', 'manufacturerbuick', 'manufacturercadillac', 'manufacturerchevrolet', 'manufacturerchrysler', 'manufacturerdodge', 'manufacturerferrari', 'manufacturerford', 'manufacturergmc', 'manufacturerhonda', 'manufacturerhyundai', 'manufacturerjeep', 'manufacturerkia', 'manufacturerland.rover', 'manufacturerlexus', 'manufacturerlincoln', 'manufacturermazda', 'manufacturermercedes.benz', 'manufacturernissan', 'manufacturerother', 'manufacturerpontiac', 'manufacturerram', 'manufacturersubaru', 'manufacturertoyota', 'manufacturervolkswagen', 'fueldiesel', 'fuelelectric', 'fuelgas', 'fuelhybrid', 'fuelother', 'transmissionautomatic', 'transmissionmanual', 'transmissionother', 'drive4wd', 'drivefwd', 'driverwd', 'sizecompact', 'sizefull.size', 'sizemid.size', 'sizesub.compact', 'typeconvertible', 'typecoupe', 'typehatchback', 'typeother', 'typepickup', 'typesedan', 'typesuv', 'typetruck', 'typevan', 'paint_colorblack', 'paint_colorblue', 'paint_colorgrey', 'paint_colorother', 'paint_colorred', 'paint_colorsilver', 'paint_colorwhite']
    for i in range(len(columns)):
        if variable_to_find.lower() in columns[i]:
            return i
    return -1

def test_get_info(query):
    """
        Description: Prints out an entire query for debugging
        Outputs: See above
    """
    columns = ['year', 'condition', 'cylinders', 'odometer', 'posting_date', 'income_this_year', 'manufactureracura', 'manufactureraudi', 'manufacturerbmw', 'manufacturerbuick', 'manufacturercadillac', 'manufacturerchevrolet', 'manufacturerchrysler', 'manufacturerdodge', 'manufacturerferrari', 'manufacturerford', 'manufacturergmc', 'manufacturerhonda', 'manufacturerhyundai', 'manufacturerjeep', 'manufacturerkia', 'manufacturerland.rover', 'manufacturerlexus', 'manufacturerlincoln', 'manufacturermazda', 'manufacturermercedes.benz', 'manufacturernissan', 'manufacturerother', 'manufacturerpontiac', 'manufacturerram', 'manufacturersubaru', 'manufacturertoyota', 'manufacturervolkswagen', 'fueldiesel', 'fuelelectric', 'fuelgas', 'fuelhybrid', 'fuelother', 'transmissionautomatic', 'transmissionmanual', 'transmissionother', 'drive4wd', 'drivefwd', 'driverwd', 'sizecompact', 'sizefull.size', 'sizemid.size', 'sizesub.compact', 'typeconvertible', 'typecoupe', 'typehatchback', 'typeother', 'typepickup', 'typesedan', 'typesuv', 'typetruck', 'typevan', 'paint_colorblack', 'paint_colorblue', 'paint_colorgrey', 'paint_colorother', 'paint_colorred', 'paint_colorsilver', 'paint_colorwhite']
    for i in range(64):
        print(columns[i], query[0,i])

def get_similar_models(model, size, year, type, cylinders, EDA_data):
    """
        Description: Retrieves the closest matches from the Craigslist database
    """
    similar = EDA_data[EDA_data['model'] == model.lower()]
    similar = similar[similar['price'] != "0.0"]
    similar = similar.drop_duplicates()
    similar = similar[similar['year'] == year]
    similar = similar.drop(columns=['income_this_year', 'posting_date', 'cylinders'])
    similar.insert(0, 'state', similar.pop('state'))
    return similar

app = Flask(__name__)

# Income.csv contains raw data, is not sorted and cleaned for training
path_to_income_csv = 'Demo_and_EDA_model_code/with_income.csv'
EDA_data = pd.read_csv(path_to_income_csv)

# one_hotted_training_data.csv is suitable for training, we filter out undesired values
one_hot_data = pd.read_csv('Demo_and_EDA_model_code/one_hotted_training_data.csv')
one_hot_data = one_hot_data[one_hot_data['price'] <= 50000]
one_hot_data = one_hot_data[one_hot_data['price'] > 1000]

# We train a new decision tree every time the server is booted, since the DT model
# is too large to put in the repo, but is fairly fast to train
train, test = train_test_split(one_hot_data, test_size=0.2)
X_train = train.drop('price', axis=1).to_numpy()
y_train = train['price'].to_numpy()
X_valid = test.drop('price', axis=1).to_numpy()
y_valid = test['price'].to_numpy()
model_Tree = DecisionTreeClassifier()
model_Tree = model_Tree.fit(X_train,y_train)

# Loading neural network model in
path_to_n_network = 'Demo_and_EDA_model_code/web_app/app/NN_model.h5'
model_NN = ks.models.load_model(path_to_n_network)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 65 columns (including price), 64 without
        query = np.zeros([1,64])

        # This section retrieves the information from the form, and creates a vector query that 
        # can be fed into the models and for searching

        # Retrieves Model info from form
        Model = request.form.get('Model')

        # Retrieves Manufacturer info from form
        Manufacturer = request.form.get('Manufacturer')
        query[0,one_hot(Manufacturer)] = 1

        # Retrieves Year info from form
        Year = int(request.form.get('Year'))
        query[0,one_hot("year")] = Year

        # Retrieves Miles info from form
        Miles = int(request.form.get('miles'))
        query[0,one_hot("odometer")] = Miles

        # Retrieves PostingDate info from form
        PostingDate = 2021
        query[0,one_hot("posting_date")] = PostingDate

        # Retrieves income_this_year info from form
        income_this_year = int(request.form.get('State_income')) # Change this to average income per state later
        query[0,one_hot("income_this_year")] = income_this_year

        # Retrieves Fuel info from form
        Fuel = request.form.get('Fuel')
        query[0,one_hot(Fuel)] = 1

        # Retrieves Condition info from form
        Condition = request.form.get('Condition')
        query[0,one_hot('condition')] = Condition

        # Retrieves Cylinders info from form
        Cylinders = request.form.get('Cylinders')
        query[0,one_hot('cylinders')] = Cylinders

        # Retrieves Transmission info from form
        Transmission = request.form.get('Transmission')
        query[0,one_hot(Transmission)] = 1

        # Retrieves Drive info from form  
        Drive = request.form.get('Drive')
        query[0,one_hot(Drive)] = 1

        # Retrieves Size info from form  
        Size = request.form.get('Size')
        query[0,one_hot(Size)] = 1

        # Retrieves vehicle type info from form  
        Type = request.form.get('Type')
        query[0,one_hot(Type)] = 1

        # Retrieves Paint type info from form  
        Paint = request.form.get('Paint')
        query[0,one_hot("color"+Paint)] = 1

        # Retrieves seller or buyer label from the form
        Seller_Type_Individual = request.form.get('Seller_Type_Individual')

        # Retrieves Zipcode
        Zipcode = request.form.get('Zipcode')

        # Retrieves data from Craigslist similar to the user election
        similar_models = get_similar_models(Model, Size, Year, Type, Cylinders, EDA_data)

        # Predictions using the decision tree and neural network
        pred_NN = model_NN.predict(query)[0,0]
        pred_Tree = model_Tree.predict(query)[0]
        preds_all = [{"pred_Tree" :pred_Tree, "pred_NN":pred_NN}]

        # Predicting the price for two years before and after the selected model year
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

        # Lowest and highest value of the decision tree predictions, used for chart sizing
        lowest = str(list_of_Tree_preds[min(list_of_Tree_preds, key=list_of_Tree_preds.get)])
        highest =  str(list_of_Tree_preds[max(list_of_Tree_preds, key=list_of_Tree_preds.get)])

        # Getting the scraped data from scraping functions (see scraper.py)
        autotrader = pd.DataFrame.from_dict(scrapeAutoTrader(str(Manufacturer), str(Model), str(int(Year)), str(int(Zipcode)), "PLACEHOLDER", "PLACEHOLDER"))
        cars = pd.DataFrame.from_dict(scrapeCars(str(Manufacturer), str(Model), str(int(Year)), str(int(Zipcode))))
        imageurl = str(get_google_img(Year, Manufacturer, Model, Paint))

        # Passes various pieces of data to the result page to be displayed in Jinja
        return render_template('resultpage.html', lowest = lowest, highest=highest,car0=list_of_Tree_preds['0'], car1=list_of_Tree_preds['1'],car2=list_of_Tree_preds['2'],car3=list_of_Tree_preds['3'],car4=list_of_Tree_preds['4'], year0 = list_of_years['0'],year1 = list_of_years['1'],year2 = list_of_years['2'],year3 = list_of_years['3'],year4 = list_of_years['4'], data=preds_all, tables = [similar_models.to_html()], autotrader=[autotrader.to_html()], cars=[cars.to_html()], image=imageurl, zip=str(Zipcode), manufacturer=str(Manufacturer), model=str(Model),color=str(Paint), year=str(Year))
    return render_template('querypage.html')

if __name__ == '__main__':
    app.run(debug=True)