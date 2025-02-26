import json
import time
from random import randint
from mangaScrape import weebCentralBase, mangakakalotBase
from weebcentral import rip_manga_ms
from mangakakalot import rip_manga_mk

def insert_to_file(new_entry):
    # managed json file
    print(new_entry)
    with open('mangaData.json', "r") as outfile:
        data = json.load(outfile)
    data.append(new_entry)
    with open('mangaData.json', "w") as outfile:
        json.dump(data, outfile, indent=4)

def download_helper(source):
    found_list_idx = []
    selected = input("Hello! Select a manga from your list to scrape: ")
    with open("mangaData.json", "r") as outfile:
        data = json.load(outfile)
    for i in range(len(data)):
        if (selected in data[i]['title'] or selected.capitalize() in data[i]["title"]):
            print("FOUND MATCH")
            if data[i]["source"] == source:
                print("FOUND MATCH AND SOURCE")
                found_list_idx.append(i)
    if len(found_list_idx) != 0:
        for i in range(len(found_list_idx)):
            print(str(i+1) + ": " + data[found_list_idx[i]]["title"])
        selected_manga_idx = input("Select a manga from your searched items: ")
        realIdx = found_list_idx[int(selected_manga_idx)-1]
        return realIdx
    else:
        print("Error, Item was not found in your list with the selected source ")
        return -1

def clean_and_strip(item):
    item = item.replace('\n', "").replace('\t', "").strip()
    return item


def download_handler(chapter_list, manga_idx):
    with open("mangaData.json", "r") as f:
        data = json.load(f)
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
                raise Exception(
                    "Error downloading the content requested: Mangasee")
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