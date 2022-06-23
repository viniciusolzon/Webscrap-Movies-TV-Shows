# This file gathers additional data such as the rating of the movie according to IMDB votes and also the director's name.
# However, I did not ended up making the csv file of it, because the scraping takes too long to do so, the reason why it's
# because the response time from the selected URL takes much longer than expected. I'm working on it.

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time

browser = webdriver.Chrome("webscraping/chromedriver")

browser.maximize_window()

browser.get('https://www.justwatch.com/us/provider/netflix/movies')

html = browser.page_source 

soup = BeautifulSoup(html, "lxml")

# Scrolling down to the bottom of the page
browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
pre_scroll_height = browser.execute_script('return document.body.scrollHeight;')
run_time, max_run_time = 0, 1

while True:
    iteration_start = time.time()
    # Scroll webpage, the 100 allows for a more 'aggressive' scroll
    browser.execute_script('window.scrollTo(0, 100*document.body.scrollHeight);')
    post_scroll_height = browser.execute_script('return document.body.scrollHeight;')
    scrolled = post_scroll_height != pre_scroll_height
    timed_out = run_time >= max_run_time

    if scrolled:
        run_time = 0
        pre_scroll_height = post_scroll_height

    elif not scrolled and not timed_out:
        run_time += time.time() - iteration_start

    elif not scrolled and timed_out:
        break

# Getting the link to obtain the desired data
links = []
elems = browser.find_elements_by_xpath("//a[@href]")
for elem in elems:
    links.append(elem.get_attribute("href"))

browser.close()

# The first 221 and last 34 links are not useful
links = links[221:len(links)-34]

# Creating lists to store movie data
movie_name = []
movie_director = []
movie_rating = []

for link in links:
    # Movie Name
    name = link[35:]
    name = name.replace("-", " ").title()
    movie_name.append(name)

browser = webdriver.Chrome("webscraping/chromedriver")

browser.maximize_window()

for link in links:
    browser.get(str(link))
    html = browser.page_source 
    soup = BeautifulSoup(html, "lxml")
    # Movie Director
    director = soup.find("a", class_ = 'title-credit-name')
    movie_director.append(director.text[1:-1])
    # IMDB rating of the movie
    rating = browser.find_element_by_xpath("//div[@class='detail-infos__value']").text
    rating = str(rating)
    rating = rating[4:]
    movie_rating.append(rating)

browser.close()
time.sleep(2)

df = pd.DataFrame()
df['Movie title'] = movie_name
df['Movie director'] = movie_director
df['IMDB rating'] = movie_rating

df.to_csv('Movie_Data.csv')
