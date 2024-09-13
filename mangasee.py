# mangasee scraping, handlers, helpers, methods
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
mangaSeeBase = "https://mangasee123.com"


def search_mangasee_helper(user_manga):
    ms_manga_results = [mangaSeeBase]
    # seperate by inserting base url at the first index before adding any data, will check for domain change, and will label as such to user
    search_url = "https://mangasee123.com/search/?name=" + user_manga
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_dne = soup.find('div', class_="NoResults")
    if manga_dne:
        print("Please enter a valid manga name, " + user_manga + " not found")
        return
    # continue and show user list of manga names and links
    manga_results = soup.find_all('a', class_="SeriesName ng-binding")
    for i in range(len(manga_results)):
        ms_manga_results.append(manga_results[i])
    return ms_manga_results
