from selenium import webdriver
from selenium.webdriver import ChromeOptions

_driver = None

def get_driver():
    global _driver
    headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

    if _driver is None:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--log-level=3")
        options.add_argument("user-agent=" + headers)
        _driver = webdriver.Chrome(options=options)
    return _driver

def close_driver():
    global _driver
    if _driver is not None:
        _driver.quit()
        _driver = None