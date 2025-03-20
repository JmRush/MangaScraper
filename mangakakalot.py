import time
from datetime import datetime
from bs4 import BeautifulSoup
from helperfunctions import clean_and_strip, insert_to_file, download_handler, download_helper, open_file, update_file
from helperfunctions import driver, mangakakalotBase



def search_manga_mk():
    user_manga = input("Enter manga: ")
    # normalizing for URL param search
    if " " in user_manga:
        user_manga = user_manga.replace(" ", "_")

    # Fetch page
    search_url = "https://mangakakalot.com/search/story/" + user_manga
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Get the element that wraps the manga containers, check if it exists
    manga_data_wrapper = soup.findAll('div', class_="story_item")
    if (manga_data_wrapper == []):
        print("Nothing found on mangakakalot, please retry your search or select from another source")
        return

    # Fetch title of manga card element, and clean it
    for i in range(len(manga_data_wrapper)):
        title_element = manga_data_wrapper[i].find('h3', class_="story_name")
        title = clean_and_strip(title_element.text)
        display_list_num = i+1
        print(str(display_list_num) + ". " + title)

    # Get the user input for which manga they want to select
    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_data_wrapper):

        #Select the title element clean it, and get the link to the selected manga
        title_element = manga_data_wrapper[int(selected_manga)-1].find('h3', class_="story_name")
        story_link = title_element.find('a')['href']
        title = clean_and_strip(title_element.text)
        print("You have selected " + title + "! ")
        print(manga_data_wrapper[int(selected_manga)-1])


        # Ask user if they want to add the manga to their library
        insertToFile = input("Would you like to insert to mangaData? : Y/N")
        #If yes, get all the metadata for the manga and create an entry
        if insertToFile == "y" or insertToFile == "Y":
            #Latest chapter released
            story_item_right = manga_data_wrapper[int(selected_manga)-1].find('div', class_="story_item_right") #named after the class wrapping the data
            story_latest_chapter_text = story_item_right.find('em', class_="story_chapter").text
            story_latest_chapter = clean_and_strip(story_latest_chapter_text).split("")[1]

            #Author and lastUpdated date
            story_data = story_item_right.findAll("span") #Element wrapping the data
            story_author = clean_and_strip(story_data[0].text.split(':')[1])
            story_last_updated = clean_and_strip(story_data[1].text.split(':')[1])
            genres, status = get_genre_and_status(story_link) #calls function that cleans, and returns the genre tags and status (ongoing/completed)

            #Creating an object with the data gathered from the webpage
            mk_data_entry = {
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
            #saving the object containing the metadata into our data file
            insert_to_file(mk_data_entry)
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
    


def get_genre_and_status(link):
    # ----------------------------------------------------------------------------------------
    #Genre and status are both found on the main endpoint of the manga, not on the search card
    # ----------------------------------------------------------------------------------------
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Mangakakalot redirects to two domains, chapmanganato and mangakakalot, so we need to check which one this specific manga redirects to
    manga_status = -1
    genre_list = []
    if ("https://mangakakalot.com" in link):
        data_container = soup.find("ul", class_="manga-info-text")
        list_items = data_container.findAll('li')

        for i in range(len(list_items)):
            item = clean_and_strip(list_items[i].text)
            if "Genres" in item:
                item = item.split(' :')
                genre_list = item[1].split(', ')
                genre_list[len(genre_list) -1] = genre_list[len(genre_list)-1].replace(",", "")
            if "Status" in item:
                item = item.split(': ')
                manga_status = item[1]

    if ("https://chapmanganato.to" in link):
        data_container = soup.find("table", class_="variations-tableInfo")
        container_rows = data_container.findAll('tr')

        for i in range(len(container_rows)):
            # find first table data in each row with the tag "status and genres"
            td = container_rows[i].find('td')
            td_desc = clean_and_strip(td.text)

            #Only capture the status and genre data, as we already have the other metadata from the search card
            if (td_desc == 'Status :'):
                status_element = container_rows[i].findAll('td')
                manga_status = clean_and_strip(status_element[1].text)
            elif (td_desc == 'Genres :'):
                genre_element_group = container_rows[i].findAll('td')
                genre_group_links = genre_element_group[1].findAll('a')
                for item in range(len(genre_group_links)):
                    genre_list.append(genre_group_links[item].text)

    return genre_list, manga_status

def get_chapter_list_mk(manga_idx):
    #Opening the file that contains the data for the manga, checking if its empty
    data = open_file("get_chapter_list_mk")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")

    #Getting the link to the selected manga
    manga_source = data[manga_idx]["link"]
    driver.get(manga_source)

    #Fetch the manga page with the chapter list and get the chapter list, using different selectors for the two domains
    chapter_list = []
    if "chapmanganato" in manga_source:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        chapter_container = soup.find('ul', class_="row-content-chapter")
        list_items = chapter_container.findAll("li", class_="a-h")

        #Fetch the links to each chapter available and append to list
        for i in range(len(list_items)):
            anchor_element = list_items[i].find('a')
            link = anchor_element['href']
            chapter_list.append(link)

    if "mangakakalot" in manga_source:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        chapter_container = soup.find('div', class_="chapter-list")
        outter_wrappers = chapter_container.findAll("div", class_="row")

        #Fetch the links to each chapter available and append to list
        for i in range(len(outter_wrappers)):
            span_container = outter_wrappers[i].find("span")
            anchor_element = span_container.find("a")
            link = anchor_element['href']
            chapter_list.append(link)

    #Send the chapter links and the index of the manga to the download handler, to save the images and update the file
    download_handler(chapter_list, manga_idx)

def update_manga_data_mk(manga_idx, data):
    #Updating some of the metadata for the manga, such as the latest chapter, last updated, and the running status
    link = data[manga_idx]["link"]
    driver.get(link)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Check which domain the manga is hosted on, and fetch the data accordingly
    if (mangakakalotBase in link):

        #Get the data wrapper for the manga, which is an UL, and create a list of the data points, the LI elements
        top_data_wrapper = soup.find("ul", "manga-info-text")
        data_points = top_data_wrapper.findAll("li")

        #Initialize variables to store the data
        status = -1
        last_updated = -1
        latest_chapter = -1

        #Loop through the data points, and check if the text contains the data we want, if it does, clean it and store it
        for point in data_points:
            if "Status" in point.text:
                status = clean_and_strip(point.text.split(":")[1])
            if "Last updated" in point.text:
                last_updated = clean_and_strip(clean_and_strip(point.text.split(":")[1]).split(" ")[0])# Cleaning the datetime of any extra characters in order to properly format it
                last_updated = datetime.strptime(last_updated, '%b-%d-%Y').strftime('%m-%d-%Y') # Formating datetime to mm-dd-yyyy
        chapter_wrapper = soup.find("div", "chapter-list") # Get the wrapper for the chapter list
        latest_chapter = chapter_wrapper.find("a").text  # Get the top chapter in the list, which is the latest


        #If everything is found, update the file
        if(chapter_wrapper != -1 and latest_chapter != -1  and status != -1):
            data[manga_idx]["lastUpdated"] = last_updated
            data[manga_idx]["lastChapter"] = latest_chapter
            data[manga_idx]["status"] = status
            update_file(data)
        else:
            raise Exception("Unable to find time updated, status or latest chapter")

    if ("chapmanganato" in link):
        #data wrappers for status, last updated, and latest chapter
        status_wrapper = soup.find("i", "info-status").parent.parent #Easiest way to grab the data was find a unique child element
        last_updated_wrapper = soup.find("i", "info-time").parent.parent #Easiest way to grab the data was find a unique child element
        latest_chapter_wrapper = soup.find("ul", "row-content-chapter")

        #getting the elements holding the data from the wrappers
        status = status_wrapper.find("td", "table-value")
        last_updated = last_updated_wrapper.find("span", "stre-value")
        latest_chapter = latest_chapter_wrapper.find("a", "chapter-name text-nowrap")

        #If the items are not "Falsy", we can grab the text from the elements and update the file
        if(status and last_updated and latest_chapter):
            status = status.text
            last_updated = last_updated.text
            latest_chapter = latest_chapter.text
            data[manga_idx]["status"] = status
            data[manga_idx]["lastChapter"] = latest_chapter
            #process date to be in the format of mm-dd-yyyy
            last_updated = clean_and_strip(last_updated.split("-")[0])
            last_updated = datetime.strptime(last_updated, '%b %d,%Y').strftime('%m-%d-%Y')
            data[manga_idx]["lastUpdated"] = last_updated
            update_file(data)
        else:
            raise Exception("Unable to find time updated, status or latest chapter")

