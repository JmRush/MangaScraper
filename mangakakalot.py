import json
import pathlib
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from random import randint
from helperfunctions import clean_and_strip, insert_to_file, download_handler, download_helper
from mangaScrape import BASE_DLPATH, driver, weebCentralBase, mangakakalotBase, headers



def search_manga_mk():
    user_manga = input("Enter manga: ")
    if " " in user_manga:
        # replace space with _ for url parameters
        user_manga = user_manga.replace(" ", "_")
    # seperate by inserting base url at the first index before adding any data, will check for domain change, and will label as such to user
    search_url = "https://mangakakalot.com/search/story/" + user_manga
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_data_list = soup.findAll('div', class_="story_item")
    if (manga_data_list == []):
        print("Nothing found on mangakakalot, please retry your search or select from another source")
        return
    # process data and then create a entry in mangadata.json
    for i in range(len(manga_data_list)):
        title = manga_data_list[i].find('h3', class_="story_name").text
        title = clean_and_strip(title)
        list_num = i+1
        print(str(list_num) + ". " + title)
    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_data_list):
        title = manga_data_list[int(
            selected_manga)-1].find('h3', class_="story_name")
        story_link = title.find('a')['href']
        title = clean_and_strip(title.text)
        print("You have selected " + title + "! ")
        print(manga_data_list[int(selected_manga)-1])
        insertToFile = input("Would you like to insert to mangaData? : Y/N")
        if insertToFile == "y" or insertToFile == "Y":
            story_item_right = manga_data_list[int(
                selected_manga)-1].find('div', class_="story_item_right")
            story_latest_chapter = story_item_right.find(
                'em', class_="story_chapter").text
            story_latest_chapter = clean_and_strip(story_latest_chapter)
            story_data = story_item_right.findAll("span")
            story_author = clean_and_strip(story_data[0].text.split(':')[1])
            story_last_updated = clean_and_strip(
                story_data[1].text.split(':')[1])
            genres, status = get_genre_status(story_link)
            mk_entry = {
                "author": story_author,
                "status": status,
                "lastChapter": story_latest_chapter,
                "lastUpdated": story_last_updated,
                "translation": "N/A",
                "title": title,
                "genres": genres,
                "type": "",
                "link": story_link,
                "source": mangakakalotBase,
                "lastRipped": -1
            }
            insert_to_file(mk_entry)
        else:
            print("Item not added to list, incorrect input or selected no")
    else:
        print("Please select a valid item from the list")
        return

def download_manga_mk():
    realIdx = download_helper(mangakakalotBase)
    if realIdx != -1:
        get_chapter_list_mk(realIdx)
    else:
        raise Exception("Index is out of bounds for MK download")
    


def get_genre_status(link):
    status = -1
    genre_list = []
    driver.get(link)
    domain = link.split("/manga")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # multiple domains that the manga redirects to
    # mangakakalot has '/manga' in it, which results in a bad split, which is resolved in my check
    if (domain[0] + '/manga' + domain[1] == "https://mangakakalot.com"):
        container = soup.find("ul", class_="manga-info-text")
        list_items = container.findAll('li')
        for i in range(len(list_items)):
            item = clean_and_strip(list_items[i].text)
            if "Genres" in item:
                item = item.split(' :')
                genre_list = item[1].split(', ')
                genre_list[len(genre_list) -
                           1] = genre_list[len(genre_list)-1].replace(",", "")
            if "Status" in item:
                item = item.split(': ')
                status = item[1]
    if (domain[0] == "https://chapmanganato.to"):
        container = soup.find("table", class_="variations-tableInfo")
        container = container.findAll('tr')
        for i in range(len(container)):
            # find first table data in each row with the tag "status and genres"
            td = container[i].find('td')
            td_desc = clean_and_strip(td.text)
            if (td_desc == 'Status :'):
                status = container[i].findAll('td')
                status = clean_and_strip(status[1].text)
            elif (td_desc == 'Genres :'):
                genre_group = container[i].findAll('td')
                genre_group = genre_group[1].findAll('a')
                for item in range(len(genre_group)):
                    genre_list.append(genre_group[item].text)
    return genre_list, status

def get_chapter_list_mk(manga_idx):
    chapter_list = []
    with open("mangaData.json", "r") as f:
        data = json.load(f)
    manga_source = data[manga_idx]["link"]
    driver.get(manga_source)
    if "chapmanganato" in manga_source:
        # row-content-chapter
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        chapter_container = soup.find('ul', class_="row-content-chapter")
        list_items = chapter_container.findAll("li", class_="a-h")
        for i in range(len(list_items)):
            anchor = list_items[i].find('a')
            link = anchor['href']
            chapter_list.append(link)
    if "mangakakalot" in manga_source:
        # chapter-list
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        chapter_container = soup.find('div', class_="chapter-list")
        outter_wrappers = chapter_container.findAll("div", class_="row")
        for i in range(len(outter_wrappers)):
            span = outter_wrappers[i].find("span")
            anchor = span.find("a")
            link = anchor['href']
            chapter_list.append(link)
    download_handler(chapter_list, manga_idx)


def rip_manga_mk(page, data, manga_idx):
    chapter_images = []
    search_url = page
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_container = soup.find('div', class_="container-chapter-reader")
    chapter_folder = ""
    # chapter folder creations
    if "chapmanganato" in data[manga_idx]['link']:
        chapter_selection = soup.find("select", class_="navi-change-chapter")
        chapter_selection = chapter_selection.find("option", selected=True)
        chapter_selection = clean_and_strip(chapter_selection.text)
        chapter_folder += chapter_selection
    elif "mangakakalot" in data[manga_idx]["link"]:
        chapter_h1 = soup.find("h1", class_="current-chapter")
        chapter_text = chapter_h1.text
        chapter_text = chapter_text.split(": ")
        for splt in chapter_text:
            if "chapter" in splt or "Chapter" in splt:
                chapter_text = clean_and_strip(splt)
                break
        chapter_folder += chapter_text
    if '-' not in chapter_folder:
        chapter_folder = "S0 - " + chapter_folder
    try:
        pathlib.Path(BASE_DLPATH + "/" + data[manga_idx]['title'] +
                     "/" + chapter_folder).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        return False
    # grabbing image from chapter
    all_images = image_container.findAll('img')
    for img in all_images:
        if (img.has_attr('title') and img):
            img_src = img.get('src')
            chapter_images.append(img_src)
    print(chapter_images)
    image_count = 0
    for image_url in chapter_images:
        referer = ""
        fileName = image_url.split('/')
        fileName = fileName[len(fileName)-1]
        if "chapmanganato" in data[manga_idx]['link']:
            referer = "https://chapmanganato.to/"
        elif "mangakakalot" in data[manga_idx]['link']:
            referer = "https://mangakakalot.com/"
        response = requests.get(image_url, headers={
                                'UserAgent': headers, 'referer': referer})
        if (response.status_code != 200):
            print("Error getting the current file")
            return False
        else:
            print("Woooo we have our images")
            with open(BASE_DLPATH + "/" + data[manga_idx]['title'] + "/" + chapter_folder + '/' + fileName, 'wb') as f:
                noop = f.write(response.content)
                print("Saved {}".format(BASE_DLPATH + "/" + data[manga_idx]['title'] +
                      "/" + chapter_folder + '/' + fileName))
        image_count += 1
        if image_count % 10 == 0:
            time.sleep(randint(9, 15))
