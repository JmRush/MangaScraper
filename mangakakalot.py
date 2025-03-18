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


    search_url = "https://mangakakalot.com/search/story/" + user_manga
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Get the element that wraps the manga containers, check if it exists
    manga_data_wrapper = soup.findAll('div', class_="story_item")
    if (manga_data_wrapper == []):
        print("Nothing found on mangakakalot, please retry your search or select from another source")
        return

    # process data and then create a entry in mangadata.json
    for i in range(len(manga_data_wrapper)):
        title_element = manga_data_wrapper[i].find('h3', class_="story_name")
        title = clean_and_strip(title_element.text)
        display_list_num = i+1
        print(str(display_list_num) + ". " + title)

    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_data_wrapper):
        title = manga_data_wrapper[int(
            selected_manga)-1].find('h3', class_="story_name")
        story_link = title.find('a')['href']
        title = clean_and_strip(title.text)
        print("You have selected " + title + "! ")
        print(manga_data_wrapper[int(selected_manga)-1])
        insertToFile = input("Would you like to insert to mangaData? : Y/N")
        if insertToFile == "y" or insertToFile == "Y":
            story_item_right = manga_data_wrapper[int(
                selected_manga)-1].find('div', class_="story_item_right")
            story_latest_chapter = story_item_right.find(
                'em', class_="story_chapter").text
            story_latest_chapter = clean_and_strip(story_latest_chapter).split("")[1]
            story_data = story_item_right.findAll("span")
            story_author = clean_and_strip(story_data[0].text.split(':')[1])
            story_last_updated = clean_and_strip(story_data[1].text.split(':')[1])
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
    data = open_file("get_chapter_list_mk")
    if data == -1 or data == None:
        raise Exception("Data is empty or not found")
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

def update_manga_data_mk(manga_idx, data):
    # we want to update latestChapter, lastUpdated, status, which will have to be done depending on the domain
    link = data[manga_idx]["link"]
    driver.get(link)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    if (mangakakalotBase in link):
        # manga-info-text
        top_wrapper = soup.find("ul", "manga-info-text")
        data_points = top_wrapper.findAll("li")
        status = -1
        last_updated = -1
        latest_chapter = -1
        for point in data_points:
            if "Status" in point.text:
                status = clean_and_strip(point.text.split(":")[1])
            if "Last updated" in point.text:
                last_updated = clean_and_strip(clean_and_strip(point.text.split(":")[1]).split(" ")[0])
                print(last_updated)
                last_updated = datetime.strptime(last_updated, '%b-%d-%Y').strftime('%m-%d-%Y')
        chapter_wrapper = soup.find("div", "chapter-list")
        latest_chapter = chapter_wrapper.find("a").text 
        if(chapter_wrapper != -1 and latest_chapter != -1  and status != -1):
            data[manga_idx]["lastUpdated"] = last_updated
            data[manga_idx]["lastChapter"] = latest_chapter
            data[manga_idx]["status"] = status
            update_file(data)
        else:
            raise Exception("Unable to find time updated, status or latest chapter")
    if ("chapmanganato" in link):
        status_wrapper = soup.find("i", "info-status").parent.parent
        last_updated_wrapper = soup.find("i", "info-time").parent.parent
        latest_chapter_wrapper = soup.find("ul", "row-content-chapter")
        status = status_wrapper.find("td", "table-value")
        last_updated = last_updated_wrapper.find("span", "stre-value")
        latest_chapter = latest_chapter_wrapper.find("a", "chapter-name text-nowrap")
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

