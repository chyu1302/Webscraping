from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import pymongo
import pprint


def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():

    browser = init_browser()

    # Visit mars.nasa.gov
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    time.sleep(1)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    list_text = soup.find('div', class_='list_text')
    news_title = list_text.find('a').text
    news_p = list_text.find('div',class_='article_teaser_body').text
    browser.quit()
    #----------------------------------------------------------------------------
    #Scrape images
    browser = init_browser()
    # Visit jpl.nasa.gov
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    time.sleep(1)
    browser.click_link_by_partial_text("FULL IMAGE")
    time.sleep(1)
    browser.click_link_by_partial_text("more info")

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    #Find the src for the image
    relative_image_path = soup.find_all('img', class_="main_image")[0]["src"]
    mars_img = "https://www.jpl.nasa.gov" + relative_image_path

    # Close the browser after scraping
    browser.quit()

    #---------------------------------------------------------------------
    #scrape weather info from twitter
    browser = init_browser()
    # Visit twitter.com
    t_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(t_url)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    #Find the src for the image
    Tweet = soup.find_all('div', class_="js-tweet-text-container")[1]

    # Close the browser after scraping
    browser.quit()

    #-------------------------------------------------------------------
    #mars_weather=Tweet.find('p',class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text
    mars_weather=Tweet.find('p').text
    # Visit space-facts.com
    table_url = "https://space-facts.com/mars/"
    facts= pd.read_html(table_url)
    # Assign the columns `['Mars_Earth_Comparison', 'Mars', 'Earth']`
    df = facts[0]
    df.columns = ['Mars_features', 'Mars', 'Earth']
    df= df.iloc[:,0:2]

    # converting to dict 
    facts_dict = df.set_index('Mars_features').T.to_dict()            

    #-----------------------------------------------------------------------------------------
    browser = init_browser()
    # Visit astrogeology.usgs.gov
    m_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(m_url)

    # Scrape page into Soup
    soup = bs(browser.html, "html.parser")
    mars_he = soup.find_all('h3')
    hemisphere_image_urls=[]
    for i in mars_he:
        i = i.get_text()
        browser.click_link_by_partial_text(i)
        soup2 = bs(browser.html, "html.parser")    
        hemisphere_image_urls.append({"title": i, "img_url":soup2.find_all('a', string='Sample')[0]['href']})
        browser.back()
    # Close the browser after scraping
    browser.quit()
    # Return results
    mars_data=  {'latest_mars_news': {'news_title': news_title,'news_p': news_p},
                'featured_mars_image': {'image': mars_img},
                'current_weather_on_mars' :{'current_weather_on_mars':mars_weather},
                'mars_facts': {'mars_facts':facts_dict},
                'hemisphere':hemisphere_image_urls}
    return mars_data

#pp = pprint.PrettyPrinter(indent=4)
# #pp.pprint(mars_data)
# #store the dictionary into Mongo database
# # Setup connection to mongodb
# conn = "mongodb://localhost:27017"
# client = pymongo.MongoClient(conn)

# # Select database and collection to use
# db = client['marsinfo']
# collection = db['mars_data']

# db.collection.insert_one(mars_data)
