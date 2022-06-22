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

# The first 220 and last 34 links are not useful
links = links[220:len(links)-34]

# Creating lists to store each and every movie data
movie_name = []

# Movie names
for link in links:
    name = link[35:len(link)]
    name = name.replace("-", " ").title()
    movie_name.append(name)

df = pd.DataFrame(movie_name)

df.to_csv('Movie_Name.csv')
