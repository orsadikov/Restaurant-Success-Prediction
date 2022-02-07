import re
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from csv import writer

my_dict = {'Manhattan': 'https://www.opentable.co.uk/new-york-restaurant-listings?covers=2&currentview=list&datetime'
                        '=2022-02-02+19%3A00&metroid=8&size=100&sort=Popularity&regionids%5B%5D=16',

           'Bronx': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort'
                    '=Popularity&source=dtp-form&areaId=geohash%3Adr5rz1tu&covers=2&dateTime=2022-02-01+19%3A00'
                    '&latitude=40.746266&longitude=-73.864072&metroId=8&regionIds=17&term=bronx',

           'Brooklyn': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort'
                       '=Popularity&source=dtp-form&areaId=geohash%3Adr5rz1tu&covers=2&dateTime=2022-02-01+19%3A00'
                       '&latitude=40.746266&longitude=-73.864072&metroId=8&regionIds=17&term=bronx',

           'Queens': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort'
                     '=Popularity&source=dtp-form&covers=2&dateTime=2022-02-01+19%3A00&latitude=40.799113&longitude'
                     '=-73.981473&metroId=8&term=queens',

           'Staten Island': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort'
                            '=Popularity&source=dtp-form&areaId=geohash%3Adr5rkusq&covers=2&dateTime=2022-02-01+19'
                            '%3A00&latitude=40.675277&longitude=-73.964785&metroId=8&regionIds=24&term=Staten+Island',
           'New Jersey - North': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort=Popularity&source=dtp-form&areaId=geohash%3Adr5qch6d&covers=2&dateTime=2022-02-02+01%3A30&latitude=40.58538&longitude=-74.13201&metroId=8&regionIds=18&term=New+Jersey+-+North',
           'Connecticut': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort=Popularity&term=Connecticut&source=dtp-form&areaId=geohash%3Adr7205fg&covers=2&dateTime=2022-02-02+01%3A30&latitude=40.80251&longitude=-74.175595&metroId=8&regionIds=22',
           'Western New York': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort=Popularity&source=dtp-form&areaId=geohash%3Adrk5s90u&covers=2&dateTime=2022-02-02+01%3A30&latitude=41.402716&longitude=-72.9259&metroId=8&regionIds=23&term=Western+New+York',
           'New Jersey - Central': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort=Popularity&term=New+Jersey+-+Central&source=dtp-form&areaId=geohash%3Adr8sme5q&covers=2&dateTime=2022-02-02+01%3A30&latitude=42.9521&longitude=-77.80058&metroId=8&regionIds=1492',
           'Upstate New York': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort=Popularity&term=Upstate+New+York&source=dtp-form&areaId=geohash%3Adr5jqmsh&covers=2&dateTime=2022-02-02+01%3A30&latitude=40.328919&longitude=-74.250847&metroId=8&regionIds=160',
           'Westchester / Hudson Valley': 'https://www.opentable.com/new-york-restaurant-listings?currentview=list&size=100&sort=Popularity&term=Westchester+%2F+Hudson+Valley&source=dtp-form&areaId=geohash%3Adre7xs3p&covers=2&dateTime=2022-02-02+01%3A30&latitude=42.827378&longitude=-73.84858&metroId=8&regionIds=77'
           }


def parse_html(html, boroughs):
    """Parse content from various tags from OpenTable restaurants listing"""
    data, item = pd.DataFrame(), {}
    soup = BeautifulSoup(html, 'lxml')

    for i, resto in enumerate(soup.find_all('div', class_='rest-row-info')):
        item['Title'] = resto.find('span', class_='rest-row-name-text').text

        booking = resto.find('div', class_='booking')
        item['Clients last day'] = re.search('\d+', booking.text).group() if booking else 'NA'

        rating = resto.find('div', class_='star-rating-score')
        item['Rating'] = float(rating['aria-label'].split()[0]) if rating else 'NA'

        reviews = resto.find('span', class_='underline-hover')
        item['Voters'] = int(re.search('\d+', reviews.text).group()) if reviews else 'NA'

        item['Price'] = int(resto.find('div', class_='rest-row-pricing').find('i').text.count('£'))
        item['Kitchen'] = resto.find('span', class_='rest-row-meta--cuisine rest-row-meta-text sfx1388addContent').text
        item['Location'] = resto.find('span',
                                      class_='rest-row-meta--location rest-row-meta-text sfx1388addContent').text
        item['Boroughs'] = boroughs
        data[i] = pd.Series(item)
    return data.T


# store Liverpool restuarant results by iteratively appending to csv file from each page
s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

with open('open_table_new_york.csv', 'w', encoding='utf8', newline='') as f:
    thewriter = writer(f)
    # header = ['Title', 'Location', 'Clients last day', 'Rating', 'Price', 'Kitchen',
    #           'Voters', 'Page', 'Boroughs']
    # thewriter.writerow(header)

for key, value in my_dict.items():
    url = value
    driver.get(url)
    page = collected = 0
    x = True
    if key == 'Connecticut':
        print('Connecticut')
    while x == True:
        sleep(1)
        new_data = parse_html(driver.page_source, key)
        if new_data.empty:
            break
        if page == 0:
            new_data.to_csv('open_table_new_york.csv', index=False, mode='a')

        elif page > 0:
            new_data.to_csv('open_table_new_york.csv', index=False, header=None, mode='a')
        page += 1
        collected += len(new_data)
        print(f'Page: {page} | Downloaded: {collected}')
        try:
            driver.find_element(By.LINK_TEXT, 'Next').click()
        except:
            print("End")
            x = False

driver.close()
