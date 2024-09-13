# mangakalot scraping, handlers, helpers, methods
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
mangakakalotBase = "https://mangakakalot.com"


def search_mangakakalot_helper(user_manga):
    mk_manga_results = [mangakakalotBase]
    # seperate by inserting base url at the first index before adding any data, will check for domain change, and will label as such to user
    search_url = "https://mangakakalot.com/search/story/${user_manga}"
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_dne = soup.find('div', class_="panel_story_list")
    return mk_manga_results


def scrape_mangakakalot():
    chapter_images = []
    search_url = "https://chapmanganato.to/manga-aa951883/chapter-613"
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_container = soup.find('div', class_="container-chapter-reader")
    all_images = image_container.findAll('img')
    for img in all_images:
        if (img.has_attr('title')):
            img_src = img.get('src')
            chapter_images.append(img_src)
    print(chapter_images)
    for image_url in chapter_images:
        response = requests.get(image_url, headers={
                                'UserAgent': headers, 'referer': "https://chapmanganato.to/"})
        if (response.status_code != 200):
            print("Error getting the current file")
            return False
        else:
            print("Woooo we have our images")
