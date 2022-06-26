from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time
import requests
import re

browser = webdriver.Chrome("webscraping/chromedriver")

browser.maximize_window()

browser.get('https://www.justwatch.com/us/provider/disney-plus/movies')

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
movie_rating = []
movie_genre = []
movie_runtime = []
movie_age_rating = []
movie_director = []

for link in links:
    html = requests.get(str(link)).text
    soup = BeautifulSoup(html, "lxml")
    # Title
    title = soup.find("div", class_ = 'title-block')
    title = title.h1.text
    title = title[1:-1]
    movie_name.append(title)
    # Debugger
    print(title)
    # IMDB rating
    i = 0
    x = soup.find_all("h3", class_ = 'detail-infos__subheading--label')
    x = x[i].text
    if (x == "Rating"):
        x = soup.find('a', {'href': re.compile('https:\/\/www\.imdb\.com\/title\/([\w\d]+)\/\?ref_=ref_ext_justwatch')})
        if (not(bool(x))):
            print("it has no ratings yet")
            movie_rating.append("NULL")
        else:
            imdb_rating = str(x.text)
            movie_rating.append(imdb_rating[1:-1])
            i+=1
    else:
        movie_rating.append("NULL")
    # Genre
    x = soup.find_all("h3", class_ = 'detail-infos__subheading--label')
    x = x[i].text
    if (x == "Genres"):
        genre = soup.find_all("div", class_ = 'detail-infos__value')
        genre = genre[i]
        genre = genre.text
        movie_genre.append(genre)
        i+=1
    else:
        movie_genre.append("NULL")
    # Runtime
    x = soup.find_all("h3", class_ = 'detail-infos__subheading--label')
    x = x[i].text
    if (x == "Runtime"):
        runtime = soup.find_all("div", class_ = 'detail-infos__value')
        runtime = runtime[i]
        runtime = runtime.text
        movie_runtime.append(runtime)
        i+=1
    else:
        movie_runtime.append("NULL")
    # Age rating
    x = soup.find_all("h3", class_ = 'detail-infos__subheading--label')
    x = x[i].text
    if (x == "Age rating"):
        age_rating = soup.find_all("div", class_ = 'detail-infos__value')
        age_rating = age_rating[i]
        age_rating = age_rating.text
        movie_age_rating.append(age_rating)
        i+=1
    else:
        movie_age_rating.append("NULL")
    # Director
    x = soup.find_all("h3", class_ = 'detail-infos__subheading--label')
    x = x[i].text
    if (x == "Director"):
        director = soup.find("a", class_ = 'title-credit-name')
        director = str(director.text)
        director = director[1:]
        movie_director.append(director)
    else:
        movie_director.append("NULL")

time.sleep(1)

df = pd.DataFrame()
df['Movie title'] = movie_name
df['IMDB rating'] = movie_rating
df['Genre'] = movie_genre
df['Runtime'] = movie_runtime
df['Age rating'] = movie_age_rating
df['Director'] = movie_director

print(df.head(20))
df.to_csv('Disney_movies.csv')
