import json
import time
from random import randint
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import pathlib
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

options = ChromeOptions()
#options.add_argument("--headless=new")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
weebCentralBase = "https://weebcentral.com"
mangakakalotBase = "https://mangakakalot.com"
headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

BASE_DLPATH = "D:/MANGA STORAGE"

def open_file(function_name):
    try:
        with open("mangaData.json", "r") as outfile:
            data = json.load(outfile)
    except FileNotFoundError:
        print("File not found, error in " + function_name)
        return -1
    except json.decoder.JSONDecodeError:
        print("Error decoding JSON, error in " + function_name)
        return -1
    except PermissionError:
        print("Permission denied, error in " + function_name)
        return -1
    except Exception as e:
        print("Unexpeced Error in opening or editing data file at: " + function_name  + " " + str(e))
        return -1 
    #end file handling
    return data

def insert_to_file(new_entry):
    try:
        with open('mangaData.json', "r") as outfile:
            data = json.load(outfile)
        data.append(new_entry)
        with open('mangaData.json', "w") as outfile:
            json.dump(data, outfile, indent=4)
    except FileNotFoundError:
        print("File not found, error in insert_to_file()")
    except json.decoder.JSONDecodeError:
        print("Error decoding JSON, error in insert_to_file()")
    except PermissionError:
        print("Permission denied, error in insert_to_file()")
    except Exception as e:
        print("Unexpeced Error in opening or editing data file at: insert_to_file(): " + str(e))

def update_file(data):
    try:
        with open('mangaData.json', "w") as outfile:
            json.dump(data, outfile, indent=4)
    except FileNotFoundError:
        print("File not found, error in update_file()")
    except json.decoder.JSONDecodeError:
        print("Error decoding JSON, error in update_file()")
    except PermissionError:
        print("Permission denied, error in update_file()")
    except Exception as e:
        print("Unexpeced Error in opening or editing data file at: update_file(): " + str(e))
    print("File updated and saved successfully")

def download_helper(source):
    found_list_idx = []
    selected = input("Hello! Select a manga from your list to scrape: ")
    data = open_file("download_helper")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")
    for i in range(len(data)):
        if (selected in data[i]['title'] or selected.capitalize() in data[i]["title"]):
            if data[i]["source"] == source:
                print("FOUND TITLE MATCH AND SOURCE")
                found_list_idx.append(i)
            else:
                print("FOUND TITLE MATCH BUT NOT SOURCE")
                return
    if len(found_list_idx) != 0:
        for i in range(len(found_list_idx)):
            print(str(i+1) + ": " + data[found_list_idx[i]]["title"])
        selected_manga_idx = input("Select a manga from your searched items: ")
        if(selected_manga_idx == "0"):
            print("Exiting download handler")
            return
        elif (int(selected_manga_idx)-1 > len(found_list_idx)-1):
            print("Error, item not found in your list with the selected source")
            return
        realIdx = found_list_idx[int(selected_manga_idx)-1]
        return realIdx
    else:
        print("Error, Item was not found in your list with the selected source: returning -1")
        return -1

def clean_and_strip(item):
    item = item.replace('\n', "").replace('\t', "").strip()
    return item


def download_handler(chapter_list, manga_idx):
    data = open_file("download_handler")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")
    download_start_idx = -1
    if data[manga_idx]['lastRipped'] == -1:
        download_start_idx = len(chapter_list)-1
    else:
        for i in range(len(chapter_list)):
            if data[manga_idx]['lastRipped'] == chapter_list[i]:
                download_start_idx = i-1
                break
    # update lastRipped each time I get a sucesss from rip_manga()
    print("Starting from: " + str(download_start_idx) +" at chapter " + chapter_list[download_start_idx])
    # we want to check if there exists x amount of pages:
    default_pages = 10
    if (download_start_idx < 0):
        print("No more chapters to gather: Last updated at " +data[manga_idx]['lastUpdated'] + " with chapter " + data[manga_idx]["lastChapter"])
        return
    # section this for loop off for each source
    if data[manga_idx]["source"] == weebCentralBase:
        for i in reversed(range(download_start_idx+1)):
            # verify that chapter_list[i] is NOT out of range
            print(chapter_list[i] + " WE ARE HERE " +str(default_pages) + " pages left")
            if (default_pages == 0):
                break
            if rip_manga_ms(chapter_list[i], data, manga_idx) != True:
                raise Exception("Error downloading the content requested: Weebcentral")
            else:
                print("Update the data with the latest lastRipped")
                data[manga_idx]['lastRipped'] = chapter_list[i]
                with open('mangaData.json', "w") as outfile:
                    json.dump(data, outfile, indent=4)
            default_pages = default_pages-1
            time.sleep(randint(29, 62))
            if (0 >= i-1) and (i-1 > len(chapter_list)):
                print("No more chapters to gather: Last updated at " +data[manga_idx]['lastUpdated'])
                raise Exception("No more chapters to gather")
    elif data[manga_idx]["source"] == mangakakalotBase:
        for i in reversed(range(download_start_idx+1)):
            print(chapter_list[i] + " WE ARE HERE " +
                  str(default_pages) + " pages left")
            if (default_pages == 0):
                break
            if rip_manga_mk(chapter_list[i], data, manga_idx) != True:
                raise Exception("Error downloading the content requested: Mangakakalot")
            else:
                print("Update the data with the latest lastRipped")
                data[manga_idx]['lastRipped'] = chapter_list[i]
                with open('mangaData.json', "w") as outfile:
                    json.dump(data, outfile, indent=4)
            default_pages = default_pages-1
            time.sleep(randint(29, 62))
            if (0 >= i-1) and (i-1 > len(chapter_list)):
                print("No more chapters to gather: Last updated at " +
                      data[manga_idx]['lastUpdated'])
                raise Exception("No more chapters to gather")

def rip_manga_ms(page, data, manga_idx):
    driver.get(page)
    chapter_images = []
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    chapter_folder_wrapper = soup.find("button", "col-span-4 lg:flex-1 btn btn-secondary")
    chapter_folder = chapter_folder_wrapper.find("span").text
    chapter_folder = clean_and_strip(chapter_folder)
    if '-' not in chapter_folder:
        chapter_folder = 'S0 - ' + chapter_folder
    time.sleep(2)
    image_elements = soup.find_all('img', class_="maw-w-full mx-auto")
    try:
        pathlib.Path(BASE_DLPATH + "/" + data[manga_idx]['title'] +"/" + chapter_folder).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("File already exists, exiting")
        return False
    # make request for each image src :)
    image_count = 0
    for img in image_elements:
        img_src = img.get('src')
        chapter_images.append(img_src)
    print(chapter_images)
    for image_url in chapter_images:
        fileName = image_url.split('/')
        fileName = fileName[len(fileName)-1]
        img_type = image_url.split('.')
        img_type = img_type[len(img_type)-1]
        host = urlparse(image_url).netloc
        if img_type != "jpg" and img_type != "png" and img_type != "jpeg":
            print("Error, image type is not supported exiting")
            return False
        response = requests.get(image_url, headers={"Host": host,'User-Agent': headers, 'Referer': "https://weebcentral.com/", 'Sec-Ch-Ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"'})
        print(response)
        if (response.status_code != 200):
            print("Error getting the current file")
            return False
        else:
            with open(BASE_DLPATH + "/" + data[manga_idx]['title'] +"/" + chapter_folder + '/' + fileName, 'wb') as f:
                noop = f.write(response.content)
                print("Saved {}".format(BASE_DLPATH + "/" + data[manga_idx]['title'] +"/" + chapter_folder + '/' + fileName))
        image_count += 1
        if image_count % 10 == 0:
            time.sleep(randint(9, 15))
    return True

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
    image_count = 0
    for image_url in chapter_images:
        referer = ""
        fileName = image_url.split('/')
        fileName = fileName[len(fileName)-1]
        if "chapmanganato" in data[manga_idx]['link']:
            referer = "https://chapmanganato.to/"
        elif "mangakakalot" in data[manga_idx]['link']:
            referer = "https://mangakakalot.com/"
        response = requests.get(image_url, headers={'User-Agent': headers, 'Referer': referer})
        if (response.status_code != 200 or response.headers['Content-Type'].startswith('image/') == False):
            print("Error getting the current file")
            return False
        else:
            print("Woooo we have our images")
            with open(BASE_DLPATH + "/" + data[manga_idx]['title'] + "/" + chapter_folder + '/' + fileName, 'wb') as f:
                noop = f.write(response.content)
                print("Saved {}".format(BASE_DLPATH + "/" + data[manga_idx]['title'] +"/" + chapter_folder + '/' + fileName))
        image_count += 1
        if image_count % 10 == 0:
            time.sleep(randint(9, 15))
