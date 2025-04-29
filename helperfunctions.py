import json
import time
from random import randint
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import os
import logging
logging.basicConfig(level=logging.INFO)

options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
weebCentralBase = "https://weebcentral.com"
mangakakalotBase = "https://mangakakalot.com"
headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

BASE_DLPATH = "D:\\MANGA STORAGE"

def open_file(function_name):
    try:
        with open("mangaData.json", "r") as outfile:
            data = json.load(outfile)
    except FileNotFoundError:
        logging.error("File not found, error in " + function_name)
        return -1
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding JSON, error in " + function_name)
        return -1
    except PermissionError:
        logging.error("Permission denied, error in " + function_name)
        return -1
    except Exception as e:
        logging.error("Unexpeced Error in opening or editing data file at: " + function_name  + " " + str(e))
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
        logging.error("File not found, error in insert_to_file()")
        exit()
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding JSON, error in insert_to_file()")
        exit()
    except PermissionError:
        logging.error("Permission denied, error in insert_to_file()")
        exit()
    except Exception as e:
        logging.error("Unexpeced Error in opening or editing data file at: insert_to_file(): " + str(e))
        exit()
    

def update_file(data):
    try:
        with open('mangaData.json', "w") as outfile:
            json.dump(data, outfile, indent=4)
    except FileNotFoundError:
        logging.error("File not found, error in update_file()")
        exit()
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding JSON, error in update_file()")
        exit()
    except PermissionError:
        logging.error("Permission denied, error in update_file()")
        exit()
    except Exception as e:
        logging.error("Unexpeced Error in opening or editing data file at: update_file(): " + str(e))
        exit()

def match_index_and_source(source):
    # ----------------------------------------------------------
    #Finding the indices of objects stored in our data file that match user input
    #returning the user selected object
    # ----------------------------------------------------------

    selected = input("Hello! Select a manga from your list to scrape: ")
    #Opening data file, and checking if it exists
    data = open_file("download_helper")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")

    #Checking if the input from the user, and the source are matched in the data file
    #Anything with the contained text, and correct source will be added to the found_item_idx
    found_item_idx = []
    for i in range(len(data)):
        if (selected in data[i]['title'] or selected.capitalize() in data[i]["title"]):
            if data[i]["source"] == source:
                found_item_idx.append(i)
            else:
                print("FOUND TITLE MATCH BUT NOT SOURCE")
                return

    #If an item is found, we will print the list of items found, and ask the user to select one
    if len(found_item_idx) != 0:

        #Print the list of items found
        for i in range(len(found_item_idx)):
            print(str(i+1) + ": " + data[found_item_idx[i]]["title"])

        #Have the user select an item from the list
        selected_manga_idx = input("Select a manga from your searched items: ")
        if(selected_manga_idx == "0"):
            print("Exiting download handler") #Selecting something that does not exist, as the items are numbered from index 0
            return
        elif (int(selected_manga_idx)-1 > len(found_item_idx)-1):
            print("Error, item not found in your list with the selected source") #Indexing error, selecting something out of bounds
            return
        realIdx = found_item_idx[int(selected_manga_idx)-1]
        return realIdx
    else:
        print("Error, Item was not found in your list with the selected source: returning -1")
        return -1



def clean_and_strip(item):
    item = item.replace('\n', "").replace('\t', "").strip()
    return item


def download_handler(chapter_list, manga_idx):
    #Opening data file, and checking if it exists
    data = open_file("download_handler")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")

    #loop through the chapters to find the lastRipped chapter that matches out stored string
    download_start_idx = -1
    if data[manga_idx]['lastRipped'] == -1:
        download_start_idx = len(chapter_list)-1
    else:
        for i in range(len(chapter_list)):
            if data[manga_idx]['lastRipped'] == chapter_list[i]:
                download_start_idx = i-1
                break


    #End program if there are no more chapters in our list
    if (download_start_idx < 0):
        print("No more chapters to gather: Last updated at " +data[manga_idx]['lastUpdated'] + " with chapter " + data[manga_idx]["lastChapter"])
        return

    #Default value is set to 10 chapters to download
    default_chapters_count = 10

    #We have to do this by source - weebcentral vs mangakakalot
    if data[manga_idx]["source"] == weebCentralBase:
        #Chapters are in reverse order, so we need to loop through the list in reverse order
        for i in reversed(range(download_start_idx+1)):
            if (default_chapters_count == 0):
                break

            #Fetch_manga_ms returns true or false, if false we raise an exception, otherwise we've suceeded on downloading the content
            if fetch_manga_ms(chapter_list[i], data, manga_idx) != True:
                raise Exception("Error downloading the content requested: Weebcentral")
                
            else:
                print("Update the data with the latest lastRipped")
                data[manga_idx]['lastRipped'] = chapter_list[i]
                update_file(data)
            default_chapters_count = default_chapters_count-1

            #Delay inbetween each call, to avoid spamming the server with requests
            time.sleep(randint(29, 62))

            #If we reach the end of the list, we raise an exception to stop the program
            if (0 >= i-1) and (i-1 > len(chapter_list)):
                print("No more chapters to gather: Last updated at " +data[manga_idx]['lastUpdated'])
                raise Exception("No more chapters to gather")

    elif data[manga_idx]["source"] == mangakakalotBase:

        for i in reversed(range(download_start_idx+1)):
            if (default_chapters_count== 0):
                break

            #Fetch_manga_mk returns true or false, if the fetch was unsuccessful we raise an exception, otherwise we've suceeded on downloading the content
            #and update the data with the latest lastRipped
            if fetch_manga_mk(chapter_list[i], data, manga_idx) != True:
                raise Exception("Error downloading the content requested: Mangakakalot")
            else:
                print("Update the data with the latest lastRipped")
                data[manga_idx]['lastRipped'] = chapter_list[i]
                update_file(data)

            default_chapters_count= default_chapters_count-1

            #Reached end of list, no more chapters to fetch
            if (0 >= i-1) and (i-1 > len(chapter_list)):
                print("No more chapters to gather: Last updated at " +data[manga_idx]['lastUpdated'])
                raise Exception("No more chapters to gather")

            #Delay inbetween each call, to avoid spamming the server with requests
            time.sleep(randint(29, 62))
            

def fetch_manga_ms(page, data, manga_idx):
    driver.get(page)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    chapter_folder_wrapper = soup.find("button", "col-span-4 lg:flex-1 btn btn-secondary")
    if chapter_folder_wrapper is None:
        chapter_folder_wrapper = soup.find("button", "col-span-3 lg:flex-1 btn btn-secondary")
    chapter_folder_text = chapter_folder_wrapper.find("span").text
    chapter_folder = clean_and_strip(chapter_folder_text)

    # Kavita folder parser requires volumes
    # This will add a volume number of 0 if there is not one already
    if '-' not in chapter_folder:
        chapter_folder = 'S0 - ' + chapter_folder

    #Fetching all images elements from the page
    image_elements = soup.find_all('img', class_="maw-w-full mx-auto")

    dir_path = os.path.join(BASE_DLPATH, data[manga_idx]['title'], chapter_folder)
    os.makedirs(dir_path, exist_ok=True)

    
    # Get all imag sources from dom elements
    image_chapter_sources = []

    for img in image_elements:
        img_src = img.get('src')
        image_chapter_sources.append(img_src)


    # Fetching and writing images, using a session, and dynamic headers
    with requests.Session() as session:
        image_count = 0
        for image_url in image_chapter_sources:
            fileName = image_url.split('/')[-1]
            image_extension = fileName.split('.')[-1]

            if image_extension.lower() not in ("jpg", "png", "jpeg"):
                print("Error, image type is not supported exiting")
                return False


            host = urlparse(image_url).netloc
            dyanmic_headers = {"User-Agent": headers, "Host": host, "Referer": "https://weebcentral.com/", 'Sec-Ch-Ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"'}
            response = session.get(image_url, headers=dyanmic_headers)

            # Check if the response was successful
            if (response.status_code != 200):
                print(f"Error: Failed to fetch {image_url}. HTTP {response.status_code}")
                return False

            # Write image
            save_path = os.path.join(BASE_DLPATH, data[manga_idx]['title'], chapter_folder, fileName)
            with open(save_path, 'wb') as f:
                f.write(response.content)

            #Log progress, and add delay for scraping so we don't spam 100's of requests in a minute
            image_count += 1
            if image_count % 10 == 0:
                print("Saved {}".format(save_path))
                time.sleep(randint(9, 15))
    return True

def fetch_manga_mk(page, data, manga_idx):
    driver.get(str(page))
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # chapter folder name creations depending on the domain Mangakakalot redirect
    chapter_folder = ""
    if "chapmanganato" in data[manga_idx]['link']:
        chapter_selection = soup.find("select", class_="navi-change-chapter")
        chapter_selection_element = chapter_selection.find("option", selected=True) #Selecting an option box with text about current chapter

        chapter_selection_text = clean_and_strip(chapter_selection_element.text)
        chapter_folder += chapter_selection_text

    elif "mangakakalot" in data[manga_idx]["link"]:
        chapter_h1 = soup.find("h1", class_="current-chapter")
        chapter_text = chapter_h1.text.split(": ")
        
        for splt in chapter_text:
            if "chapter" in splt or "Chapter" in splt:
                chapter_text = clean_and_strip(splt)
                break

        chapter_folder += chapter_text
    

    #Checking if the chapter folder has a volume number, if not we add one S0 for the kavita file parser
    if '-' not in chapter_folder:
        chapter_folder = "S0 - " + chapter_folder


    #Creating the needed directories for the chapters
    dir_path = os.path.join(BASE_DLPATH, data[manga_idx]['title'], chapter_folder)
    os.makedirs(dir_path, exist_ok=True)


    #Fetching all image elements from the page and storing them in 
    image_chapter_sources = []
    image_container = soup.find('div', class_="container-chapter-reader")
    all_images = image_container.findAll('img')
    for img in all_images:
        if (img.has_attr('title') and img):
            img_src = img.get('src')
            image_chapter_sources.append(img_src)

    #Fetching and writing images, using a session, and dynamic headers
    with requests.Session() as session:
        image_count = 0
        for image_url in image_chapter_sources:
            #Getting the file name from the image url            
            fileName = image_url.split('/')[-1]
            image_extension = fileName.split('.')[-1]
 
            if image_extension.lower() not in ("jpg", "png", "jpeg"):
                print("Error, image type is not supported exiting")
                return False
    
            #Selecting referer dyanmically based on the domain - mangakakalot uses mutliple domains to host the manga metadata
            #referer changes based on the domain
            referer = ""
            if "chapmanganato" in data[manga_idx]['link']:
                referer = "https://chapmanganato.to/"
            elif "mangakakalot" in data[manga_idx]['link']:
                referer = "https://mangakakalot.com/"


            response = session.get(image_url, headers={'User-Agent': headers, 'Referer': referer})
            if (response.status_code != 200):
                print("Error getting the current file")
                return False

            # Write image
            save_path = os.path.join(BASE_DLPATH, data[manga_idx]['title'], chapter_folder, fileName)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            #Log progress and add a delay for scraping so we don't spam 100's of requests in a minute
            image_count += 1
            if image_count % 10 == 0:
                print("Saved {}".format(save_path))
                time.sleep(randint(9, 15))
    