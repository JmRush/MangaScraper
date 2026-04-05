from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from datetime import datetime, date
from urllib.parse import quote
from helperfunctions import insert_to_file, download_handler, match_index_and_source, clean_and_strip, open_file, update_file
from helperfunctions import driver, weebCentralBase

def search_manga_ms():
    #Fetch the page the user requests
    user_manga = input("Enter manga: ")
    user_manga = quote(user_manga)
    search_url = f'https://weebcentral.com/search/?text={user_manga}&sort=Best+Match&order=Ascending&official=Any&anime=Any&adult=Any&display_mode=Full+Display'
    driver.get(search_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Check if there are any results on the page
    not_found = False
    manga_dne = soup.findAll('span')
    for span in manga_dne:
        if span.text == "No results found":
            not_found = True
    if not_found == True:
        print("Manga not found, please try a different search: ")
        return


    #Get all the manga cards on the page
    unsorted_manga_results = soup.find_all('a', class_="link link-hover")
    unsorted_manga_results_secondary_class = soup.find_all('a', class_="line-clamp-1 link link-hover") #Sometimes the class is different, so we extend the original array to get all posibilities
    unsorted_manga_results.extend(unsorted_manga_results_secondary_class)

    #Filter out the selected items that are not manga, and store the rest in a new array
    manga_results = []
    for manga in unsorted_manga_results:
        if "https://weebcentral.com/series/" in manga['href']:
            manga_results.append(manga)

    print(manga_results)
    #Print out the manga results
    for i in range(len(manga_results)):
        list_num = i+1
        print(str(list_num) + ". " + manga_results[i].text)

    #Ask the user to select a manga from the list, and then parse and add the data to the data file
    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_results):
        print("You have selected " +manga_results[int(selected_manga)-1].text + "! ")
        #Ask the user if they want to add the manga to their library
        answer = input("Would you like to add this manga to your library? Y/N: ")
        if answer == "Y" or answer == "y":
            selected_manga_title = manga_results[int(selected_manga)-1].text
            print(selected_manga_title)
            print("--------------------")


            #Get the parent wrapper of the selected manga, which we will send to the create_entry function
            manga_parent_wrapper = manga_results[int(selected_manga)-1].parent.parent.parent

            #Get the data fields of the manga (genre tags), which we will process here, and then send to the create_entry function
            manga_data_fields = manga_parent_wrapper.findAll("div", "opacity-70")
            manga_genre_tags = []
            for manga in manga_data_fields:
                header_tag = manga.find("strong")
                header = header_tag.text
                if "Tag(s):" in header:
                    manga_genre_tags = header_tag.parent.findAll("span")
            create_entry_ms(selected_manga_title,manga_parent_wrapper, manga_genre_tags, manga_results[int(selected_manga)-1]['href'], weebCentralBase)

        else:
            print("Item not added")
            return
    else:
        print("Please choose a correct index, the current index is out of range")
        return


def create_entry_ms(selectedTitle, selectedManga, manga_genre_tags, search_url, base_url):
    cleanData = []
    cleanGenreTags = []
    raw_manga_data = selectedManga.findAll('div', "opacity-70")
    #Loop through the raw manga data, found in the elements with the class "opacity-70"
    for selection in raw_manga_data:
        label = selection.find("strong") #These are the labels for the data, such as "Released:", "Status:", and "Type:"
        if "Tag(s):" in label: #Skipping the genre tags, as we already have them
            continue
        data = selection.findAll("span") #These are the actual data fields, such as "2014", "Ongoing", and "Manga"
        fullData = ""
        for datum in data:
            fullData += datum.text
        cleanData.append(fullData) #These are always oragnized in the same order, so we can just append them to the array, and access them by index later


    #These items do not have a date, so our date will be when this was added to the library
    today = date.today()
    todayF = today.strftime("%m-%d-%Y")
    

    #Get the author of the manga, if it exists
    author = selectedManga.find("a", "link link-info link-hover")
    if author == None:
        author = "Unknown"
    else:
        author = author.text

    #Loop through the genre tags, and clean them up
    for genreTag in manga_genre_tags:
        tag = clean_and_strip(genreTag.text)
        tag = tag.replace(",", "")
        cleanGenreTags.append(tag)

    #Check if the translation is official or not by checking the title of the abbr tag (its an icon that shows up next to the title)
    if selectedManga.find("abbr") is not None:
        translation = selectedManga.find("abbr")["title"]
        if "Official Translation" in translation:
            translation = "Official Translation"
        else:
            translation = "Not Official Translation"
    else:
        translation = "N/A"

    #Create the new entry, and add it to the data file
    new_entry = {
        "author": author,
        "released": cleanData[0], #always the first item in the array
        "status": cleanData[1], #always the second item in the array
        "lastChapter": -1,
        "lastUpdated": todayF,
        "translation": translation,
        "title": selectedTitle,
        "genres": cleanGenreTags,
        "type": cleanData[2], #always the third item in the array
        "link": search_url,
        "source": base_url,
        "lastRipped": -1
    }
    insert_to_file(new_entry)


def download_index_manga_ms():
    realIdx = match_index_and_source(weebCentralBase)
    if realIdx != -1:
        get_chapter_list_ms(realIdx)
    else:
        raise Exception("Index is out of bounds for MS download")
    

def get_chapter_list_ms(manga_idx):
    data = open_file("get_chapter_list_ms")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")

    #Use the link from the data file to get the chapter list
    driver.get(data[manga_idx]["link"])

    #Using the selenium driver, we need to click the expand button to get the full chapter list
    expand_button = driver.find_element(By.ID, "chapter-list")
    expand_button = expand_button.find_element(By.TAG_NAME, "button")
    expand_button.click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Fetch chapter list links from the page
    chapter_list = []
    chapter_wrapper = soup.find(id="chapter-list")
    anchor_tags = chapter_wrapper.find_all('a', class_="hover:bg-base-300 flex-1 flex items-center p-2")
    for i in range(len(anchor_tags)):
        chapter_list.append(anchor_tags[i]['href'])#.replace("-page-1", ""))

    #Send the chapter list to the download handler
    download_handler(chapter_list, manga_idx)

def update_manga_data_wc(manga_idx, data):
    page = data[manga_idx]["link"]
    driver.get(page)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')


    chapter_wrapper = soup.find(id="chapter-list")

    #Get the latest chapter
    latest_chapter_wrapper = chapter_wrapper.find('a', class_="hover:bg-base-300 flex-1 flex items-center p-2")
    latest_chapter = latest_chapter_wrapper.find("span", "grow flex items-center gap-2").find("span").text

    #Fetch the latest time, and format it
    latest_time_data = latest_chapter_wrapper.find('time', "opacity-50")["datetime"]
    latest_time_date_time = datetime.strptime(latest_time_data, "%Y-%m-%dT%H:%M:%S.%fZ")
    latest_time = latest_time_date_time.strftime("%m-%d-%Y")

    #Fetch the status of the manga
    status_wrapper_element = soup.findAll("ul", "flex flex-col gap-4")[0]
    status_data_elements = status_wrapper_element.findAll("a", "link link-info link-hover")
    status = -1
    for datum in status_data_elements:
        if "Ongoing" in datum.text:
            status = "Ongoing"
        elif "Completed" in datum.text:
            status = "Completed"
        elif "Hiatus" in datum.text:
            status = "Hiatus"
        elif "Canceled" in datum.text:
            status = "Canceled"


    #If all the data fetched exists, update the data file
    if(latest_time and latest_chapter and status != -1):
        data[manga_idx]["lastChapter"] = latest_chapter
        data[manga_idx]["lastUpdated"] = latest_time
        data[manga_idx]["status"] = status
        update_file(data)
    else:
        raise Exception("Latest chapter, time, or status is not found")
