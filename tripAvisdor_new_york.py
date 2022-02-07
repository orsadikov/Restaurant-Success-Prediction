import re
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from csv import writer


def parse_html(html):
    """Parse content from various tags from OpenTable restaurants listing"""
    data, item = pd.DataFrame(), {}
    soup = BeautifulSoup(html, 'lxml')



    title = soup.find_all("div", class_="emrzT Vt o")

    for i, resto in enumerate(soup.find_all("div", class_="emrzT Vt o")):

        s = resto.find('a', class_='bHGqj Cj b').text
        index = s.find(".")
        x = ""
        if index > -1:
            index += 1
            s = s[index:]
        item['Title'] = s
        rating = resto.find('svg', class_='RWYkj d H0')
        item['Rating TripAvisdor'] = float(rating['aria-label'].split()[0]) if rating else 'NA'
        s = resto.find('span', class_='ceUbJ').text
        numeric_filter = filter(str.isdigit, s)
        numeric_string = "".join(numeric_filter)
        item['Voters TripAvisdor'] = numeric_string

        data[i] = pd.Series(item)
    return data.T


# store Liverpool restuarant results by iteratively appending to csv file from each page
s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

with open('tripavisdor_new_york.csv', 'w', encoding='utf8', newline='') as f:
    thewriter = writer(f)
    # header = ['Title', 'Location', 'Clients last day', 'Rating', 'Price', 'Kitchen',
    #           'Voters', 'Page', 'Boroughs']
    # thewriter.writerow(header)

    url = 'https://www.tripadvisor.com/Restaurants-g60763-New_York_City_New_York.html'
    driver.get(url)
    page = collected = 0
    x = True

    while x == True:
        sleep(3)
        new_data = parse_html(driver.page_source)
        if new_data.empty:
            break
        if page == 0:
            new_data.to_csv('tripavisdor_new_york.csv', index=False, mode='a')

        elif page > 0:
            new_data.to_csv('tripavisdor_new_york.csv', index=False, header=None, mode='a')
        page += 1
        collected += len(new_data)
        print(f'Page: {page} | Downloaded: {collected}')
        try:
            driver.find_element(By.LINK_TEXT, 'Next').click()
        except:
            print("End")
            x = False

driver.close()
