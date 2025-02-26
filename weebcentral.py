import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from random import randint
from datetime import date
from urllib.parse import quote
from helperfunctions import insert_to_file, download_handler, download_helper, clean_and_strip
from helperfunctions import BASE_DLPATH, driver, weebCentralBase,  headers

def search_manga_ms():
    not_found = False
    user_manga = input("Enter manga: ")
    user_manga = quote(user_manga)
    search_url = f'https://weebcentral.com/search/?text={user_manga}&sort=Best+Match&order=Ascending&official=Any&anime=Any&adult=Any&display_mode=Full+Display'
    driver.get(search_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_dne = soup.findAll('span')
    for span in manga_dne:
        if span.text == "No results found":
            not_found = True
    if not_found == True:
        print("Manga not found, please try a different search: ")
        return
    # continue and show user list of manga names and links
    unsorted_manga_results = soup.find_all('a', class_="link link-hover")
    unsorted_manga_results_2 = soup.find_all('a', class_="line-clamp-1 link link-hover")
    unsorted_manga_results.extend(unsorted_manga_results_2)
    manga_results = []
    for manga in unsorted_manga_results:
        if "https://weebcentral.com/series/" in manga['href']:
            manga_results.append(manga)
    for i in range(len(manga_results)):
        list_num = i+1
        print(str(list_num) + ". " + manga_results[i].text)
    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_results):
        print("You have selected " +
              manga_results[int(selected_manga)-1].text + "! ")
        answer = input("Would you like to add this manga to your library? Y/N: ")
        if answer == "Y" or answer == "y":
            selected_manga_title = manga_results[int(selected_manga)-1].text
            print(selected_manga_title)
            print("--------------------")
            # send title and genre seperately than the rest of raw data
            manga_parent_wrapper = manga_results[int(
                selected_manga)-1].parent.parent
            manga_data_fields = manga_parent_wrapper.findAll("div", "opacity-70")
            manga_genre_tags = []
            for manga in manga_data_fields:
                header_tag = manga.find("strong")
                header = header_tag.text
                if "Tag(s):" in header:
                    manga_genre_tags = header_tag.parent.findAll("span")
            print(manga_genre_tags)
            create_entry_ms(selected_manga_title,
                            manga_parent_wrapper, manga_genre_tags, manga_results[int(
                                selected_manga)-1]['href'], weebCentralBase)

        else:
            print("Item not added")
            return
    else:
        print("Please choose a correct index, the current index is out of range")

def create_entry_ms(selectedTitle, selectedManga, manga_genre_tags, search_url, base_url):
    # check if selected title is saved in file, if not go for it!
    raw_manga_data = selectedManga.findAll('div', "opacity-70")
    cleanData = []
    cleanGenreTags = []
    # loop through this array and get text for author, year, status, latest chapter (and date updated) and genres (AND LINK)
    # year status, genres
    for selection in raw_manga_data:
        label = selection.find("strong")
        if "Tag(s):" in label:
            continue
        data = selection.findAll("span")
        fullData = ""
        for datum in data:
            fullData += datum.text
        cleanData.append(fullData)
    today = date.today()
    todayF = today.strftime("%m-%d-%Y")
    author = selectedManga.find("a", "link link-info link-hover").text
    for genreTag in manga_genre_tags:
        tag = clean_and_strip(genreTag.text)
        tag = tag.replace(",", "")
        cleanGenreTags.append(tag)
    translation = selectedManga.find("abbr")["title"]
    if "Official Translation" in translation:
        translation = "Official Translation"
    else:
        translation = "Not Official Translation"

    new_entry = {
        "author": author,
        "released": cleanData[0],
        "status": cleanData[1],
        "lastChapter": -1,
        "lastUpdated": todayF,
        "translation": translation,
        "title": selectedTitle,
        "genres": cleanGenreTags,
        "type": cleanData[2],
        "link": search_url,
        "source": base_url,
        "lastRipped": -1
    }
    insert_to_file(new_entry)


def download_manga_ms():
    realIdx = download_helper(weebCentralBase)
    if realIdx != -1:
        get_chapter_list_ms(realIdx)
    else:
        raise Exception("Index is out of bounds for MS download")
    

def get_chapter_list_ms(manga_idx):
    chapter_list = []
    with open("mangaData.json", "r") as f:
        data = json.load(f)
    driver.get(data[manga_idx]["link"])
    expand_button = driver.find_element(By.ID, "chapter-list")
    expand_button = expand_button.find_element(By.TAG_NAME, "button")
    expand_button.click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    chapter_wrapper = soup.find(id="chapter-list")
    anchor_tags = chapter_wrapper.find_all('a', class_="hover:bg-base-300 flex-1 flex items-center p-2")
    for i in range(len(anchor_tags)):
        chapter_list.append(anchor_tags[i]['href'])#.replace("-page-1", ""))
    download_handler(chapter_list, manga_idx)
