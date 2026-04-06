# MangaScraper
This is a personal project I created for my own use. Use it at your own discretion and please do so responsibly

## Disclaimer 
Disclaimer: Please use this project responsibly and ethically. These websites provide content for free, and excessive or improper scraping may violate their terms of service. This project is intended for personal use only and may break at any time due to changes in website structures, as web scraping is inherently fragile.

## Background
I maintain a NAS that stores a large collection of books and manga. This project allows me to scrape two sources, download manga/manhwa images in order, and track all downloaded content. It also keeps track of all the manga/manhwa the user downloads, along with a set of metadata that is used to update, download, and search for new reading material. I populate my NAS reader with the results of this project on a daily basis!
## Features
- Search for manga/manhwa on weebcentral and mangakakalot
- Save metadata of manga/manhwa
- Download chapters sequentially based on the saved reading list
- Automatically track the last completed chapter, allowing seamless continuation
- Organizing files in compliance with [Kavita's](https://www.kavitareader.com/) file system
- Updating metadata of selected saved material in the mangaData.json file
- Viewing your entire collection!
## Requirements
- A computer and internet access
- A storage solution with enough space for potentially hundreds of images per chapter.
- A reader - I personally use [kavita](https://www.kavitareader.com/), which I highly recommend
- ⚠️ **THIS PROJECT IS DESIGNED FOR KAVITA's file parsing system** Your experience may vary with other readers
- python3
- beautifulsoup
- selenium
- requests
- python-dotenv
- [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) use the most up to date STABLE version available for your OS
## Steps to setup
1. Install [python](https://www.python.org/downloads/) and follow the download instructions
2. Clone the repository
```
git clone https://github.com/JacobMRush/MangaScraper.git
cd MangaScraper
```
3. Install Dependencies
- (A) Install dependencies directly
```
pip install beautifulsoup4 selenium requests python-dotenv
```
- (B) Use python's virtual environment - RECOMMENDED
```
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```
## Usage
- Using Directly installed dependencies 3(A)
```sh
    python mangaScrape.py
```
- Using python's virtual environment 3(B)
```
venv/Scripts/activate
python mangaScraper.py
```
