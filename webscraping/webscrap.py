from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time

browser = webdriver.Chrome("webscraping/chromedriver")

browser.get("https://www.justwatch.com/us/provider/netflix/movies")

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

time.sleep(3)

html = browser.page_source

soup = BeautifulSoup(html, "lxml")

#Creating a list to store the data
movie_name = []

#Scraping the data
movie_data = soup.findAll("picture", attrs = {"class":"title-poster__image"})

for div in soup.find_all('picture', 'title-poster__image'):
    for img in div.find_all('img', alt=True):
        movie_name.append(img['alt'])

browser.close()

df = pd.DataFrame(movie_name)

df.to_csv('Movie_Names.csv')
