import os
import time

from selenium import webdriver
import requests
import io
from PIL import Image
from selenium.webdriver.common.by import By

from count_images import count_files_in_directory

item_start = count_files_in_directory('images')
item_end = item_start + 50
def get_google_images_url(search_term):
    formatted_search_term = search_term.replace(' ', '+')
    return f"https://www.google.com/search?q={formatted_search_term}&source=lnms&tbm=isch"

def get_wiki_images_url(search_term):
    formatted_search_term = search_term.replace(' ', '_')
    return f"https://oldschool.runescape.wiki/w/{formatted_search_term}"

def download_image(download_path, url, file_name):
    file = None
    try:
        print(f"Downloading image: {url}")
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        image.save(f"{download_path}/{file_name}")

        file = open(f"{download_path}/{file_name}", "wb")
        file.write(image_content)
        file.flush()
        os.fsync(file.fileno())
    except Exception as e:
        print(f"Failed to download image: {url}")
        print(e)
    finally:
        if file is not None:
            file.close()


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


for i, (name, icon) in enumerate(data.items()):
    if i < item_start:
        continue
    elif i >= item_end:
        break
    try:
        driver.get(get_wiki_images_url(name))
        time.sleep(1)
        print(f"Searching for {name}")
        descriptions = driver.find_elements(By.CLASS_NAME, "mw-file-description")
        print(f'Found {len(descriptions)} descriptions for {name}')
        for description in descriptions:
            try:
                thumbnail = description.find_element(By.CLASS_NAME, "mw-file-element")
                print(f'Found source: {thumbnail.get_attribute("src")}')
                if thumbnail.get_attribute("src") is not None and 'detail' in thumbnail.get_attribute("src"):
                    download_image("images", thumbnail.get_attribute("src"), f"{name}.png")
                    print(f"Downloaded {name}")
                    break
            except Exception as e:
                print(f"Failed to find thumbnail for {name}")
                print(e)
                continue
    except Exception as e:
        print(f"Failed to find {name}")
        print(e)
        continue

# Close the browser
driver.quit()
