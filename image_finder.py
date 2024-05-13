import os
import time

from selenium import webdriver
import requests
import io
from PIL import Image
from selenium.webdriver.common.by import By


def get_google_images_url(search_term):
    formatted_search_term = search_term.replace(' ', '+')
    return f"https://www.google.com/search?q={formatted_search_term}&source=lnms&tbm=isch"

def get_wiki_images_url(search_term):
    formatted_search_term = search_term.replace(' ', '_')
    return f"https://oldschool.runescape.wiki/w/{formatted_search_term}"

def download_image(download_path, url, file_name):
    try:
        print(f"Downloading image: {url}")
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        image.save(f"{download_path}/{file_name}")

        with open(f"{download_path}/{file_name}", "wb") as file:
            file.write(image_content)
    except Exception as e:
        print(f"Failed to download image: {url}")
        print(e)


# setup the Chrome driver
chromedriver_path = "/Users/marchilles/Desktop/OSRS-Image-Scraper/chromedriver_mac64/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver_path
driver = webdriver.Chrome()

# Retrieve required data
raw = {}
response = requests.get('https://prices.runescape.wiki/api/v1/osrs/mapping')
if response.status_code == 200:
    # Parse the JSON response into a Python dictionary
    raw = response.json()
else:
    print(f"Failed to get data from API, status code: {response.status_code}")

# select only name and icon from data into filtered dictionary
data = {}
for item in raw:
    if 'name' in item and 'icon' in item:
        data[item['name']] = item['icon']

# scrape images from wiki
# for name, icon in data.items():
#     driver.get(get_wiki_images_url(name))
#     # find element where alt includes name
#     # thumbnail = driver.find_elements(By.XPATH, "//a[@class='mw-file-description']//img[@class='mw-file-element']")
#     thumbnails = driver.find_elements(By.CLASS_NAME, 'mw-file-element')
#     # print(f'Found {len(thumbnails)} thumbnails for {name}')
#     for thumbnail in thumbnails:
#         if thumbnail.get_attribute("src") is not None and 'thumb' in thumbnail.get_attribute("src"):
#             download_image("images", thumbnail.get_attribute("src"), f"{name}.png")
#             break


for name, icon in data.items():
    driver.get(get_wiki_images_url(name))
    print(f"Searching for {name}")
    thumbnail = driver.find_element(By.XPATH, "//a[@class='mw-file-description']//img[@class='mw-file-element']")
    print(f'found source: {thumbnail.get_attribute("src")}')
    if thumbnail.get_attribute("src") is not None and 'thumb' in thumbnail.get_attribute("src"):
        download_image("images", thumbnail.get_attribute("src"), f"{name}.png")










# Close the browser
driver.quit()
