from weebcentral import search_manga_ms, download_index_manga_ms, update_manga_data_wc
from mangakakalot import search_manga_mk, download_manga_mk, update_manga_data_mk
from utils import weebCentralBase, mangakakalotBase
from storage_utils import open_file

def view_manga():
    data = open_file("view_manga")
    if data == None or data == -1:
        raise Exception("Data is empty or not found")
    item_number = 0
    for item in range(len(data)):
        item_number += 1
        print(str(item_number) + ": " +
              data[item]['title'] + " at index " + str(item_number-1))
    return data

def view_manga_data():
    data = view_manga()
    selected_manga = input("Select a manga to get more details: ")
    selected_manga = int(selected_manga) - 1
    print("Here is some information on the manga you selected: ")
    print("-------------------------------")
    print(data[selected_manga]['title'])
    print(data[selected_manga]['status'])
    print(data[selected_manga]['lastUpdated'])
    print(data[selected_manga]['lastChapter'])
    print(data[selected_manga]['lastRipped'])
    print("-------------------------------")

def update_manga_data():
    view_manga()
    data = open_file("update_manga_data")
    if data == None or data == -1:
        raise Exception("Data is empty or not found")
    selected_manga = input("Select a manga to update: ")
    selected_manga = int(selected_manga) - 1
    if(selected_manga < 0 or selected_manga >= len(data)):
        raise Exception("Invalid manga selected")
    print("Here is some information on the manga you selected: ")
    print("-------------------------------")
    print(data[selected_manga]['title'])
    print(data[selected_manga]['source'])
    print(data[selected_manga]['lastRipped'])
    if(data[selected_manga]["source"] == weebCentralBase):
        update_manga_data_wc(selected_manga, data)
    elif(data[selected_manga]["source"] == mangakakalotBase):
        update_manga_data_mk(selected_manga, data)



def main():
    print("Hello, welcome and select your required operation")
    print("1. View manga list")
    print("2. Search/Select Manga - Weebcentral")
    print("3. Search/Select Manga - Mangakakalot")
    print("4. Update Manga data")
    print("5. Download Manga - Weebcentral")
    print("6. Download Manga - Mangakakalot")

    selection = input()

    match selection:
        case "1":
            view_manga_data()
        case "2":
            search_manga_ms()
        case "3":
            search_manga_mk()
        case "4":
            update_manga_data()
        case "5":
            download_index_manga_ms()
        case "6":
            download_manga_mk()
        case _:
            print("Oops nothing matches your selected item!")


main()
