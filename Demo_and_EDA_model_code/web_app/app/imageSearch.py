####################################################
#                                                  #
# Author(s): Car Price Prediction Group - Zachary  #
#            Burpee, Ming Liu, Napasorn Phongphaew #
# Class: Big Data Analytics Final Project          #
# Professor: Professor Ching-Yung Lin              #
# Description: Webscraping tool to scrape the      #
#              most relevant image of a car that   #
#              is searched by the user             #
#                                                  #
####################################################

from bs4 import BeautifulSoup
import requests

def get_google_img(year, make, model, color):
    '''
    Description: Query google images for first result of a car year, make, model and color and return 
        first result that is an image
    Inputs: 
        - Year (string): Car year, number format "2022", of a valid car year
        - Make (string): Car make, lowercase, has to be a valid make
        - Model (string): Car model, lowercase, has to be a valid model of a car make
        - Color (string): Car color, lowercase, has to be a valid color of a car
    Outputs:
        - Image URL (string): A URL that extracts the image to be put into the front-end
    '''

    # Create custom URL on Google Images
    url = "https://www.google.com/search?q={}+{}+{}+{}&tbm=isch&source".format(year, make, model, color)

    # Get URL elements
    html = requests.get(url).text

    # Extract XML elements of URL
    soup = BeautifulSoup(html, 'lxml')
    # Find all image elements
    image = soup.find("img", {"alt" : ""})
    
    # Return first image element source image URL
    return image['src']


if __name__ == '__main__':
    year = '2017'
    make = 'toyota'
    model = 'camry'
    color = "red"
    print(get_google_img(year, make, model, color))