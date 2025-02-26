from weebcentral import search_manga_ms, download_manga_ms
from mangakakalot import search_manga_mk, download_manga_mk
from helperfunctions import open_file

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


def main():
    print("Hello, welcome and select your required operation")
    print("1. View manga list")
    print("2. Search/Select Manga - Mangasee")
    print("3. Search/Select Manga - Mangakakalot")
    print("4. Update Manga data")
    print("5. Download Manga - Mangasee")
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
            pass
        case "5":
            download_manga_ms()
        case "6":
            download_manga_mk()
        case _:
            print("Oops nothing matches your selected item!")


main()
