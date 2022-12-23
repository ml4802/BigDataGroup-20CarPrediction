# Group 202212-20 (US Craigslist Car Sale Data Analysis and price modeling) 
Ming Liu ml4802  
Zach Burpee zcb2110  
Napasorn Phongphaew np2839

# Summary 
Our project aims to use online used-car listing data to help customers decide the best
time to sell or buy their vehicle. To this objective, we created a web application
that, once given some information about a car, will predict the fairest price for the 
car based on previous listings, predict similar car prices for bracketing model years,
scrape existing listings and their links/pricing, and more. 

## How to run web demo:
    Run app.py inside web_app, and navigate to http://127.0.0.1:5000
    to view the webpage
    Must run on tensorflow-enabled computer

## How to process raw Kaggle data:
    See data_processing.R for instructions on how to transform Craigslist
    Kaggle dataset into data_with_income.csv, and one_hotted_training_data.csv
    Dataset used to train models and generate R is at
    https://www.kaggle.com/datasets/austinreese/craigslist-carstrucks-data
    called Vehicles.csv

# Tree with summary
Demo_and_EDA_model_code
    /web_app
        /templates
            querypage.html (Landing page)
            resultpage.html (Result page)
        app.py (Main Flask server to run)
        imageSearch.py (Image search code)
        NN_model.h5 (Trained Tensorflow NN)
        scraper.py (Webscraper for Cars.come and Autotrader)
    data_processing.R (Processes raw Kaggle data)
    data_with_income.csv (Data without one-hotting)
    EDA for Kaggle Dataset.ipynb (Data visualization and analysis)
    ML & DL Models.ipynb (Generate the models)
    one_hotted_training_data.csv (Data with one-hotting)
    state_income.csv (Used in data_processing)
