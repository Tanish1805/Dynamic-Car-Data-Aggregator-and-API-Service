from bs4 import BeautifulSoup
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2


def open_browser(url):
    
    driver_path = ChromeDriverManager().install()
    # Use the Service object with the executable path
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    
    # Pass the Service object to the webdriver.Chrome constructor
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    driver.maximize_window()
    return driver

def close_browser(browser):
    browser.quit()

def scroll_to_bottom(browser):
    # Scroll to the bottom of the page to load more content
    actions = ActionChains(browser)
    actions.send_keys(Keys.END).perform()

# Scrape the Data
def scrape_data(browser):
    page_source = browser.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    car_title_list = []
    car_price_list = []

    # Find all div elements with the specified class
    total_cars = soup.find_all('div', class_="new__car__column__lists no-ssr-list")

    # Iterate through each div with the specified class
    for car_column in total_cars:
        # Find div elements with the specified class under each car_column
        cars = car_column.find_all('div', class_="col-md-12 col-lg-4")

        # Iterate through each car div
        for car in cars:
            # Extract car title and price
            row_title = car.find('div', class_="new__car__title d-flex align-items-center")
            row_price = car.find('div', class_="new__car__price")
            
            # Extract car title
            car_title = row_title.find('a')['title'] if row_title else "N/A"

            # Extract car price
            car_price = row_price.get_text(strip=True, separator=' ').replace("View Seller Details", "") if row_price else "N/A"

            car_title_list.append(car_title)
            car_price_list.append(car_price)

    # Return all the lists
    return car_title_list, car_price_list


def write_to_file(car_title_list, car_price_list):
    with open('carsData.txt', 'w', encoding='utf-8') as file:
        for title, price in zip(car_title_list, car_price_list):
            file.write(f"{title}\n{price}\n")
    
    print("Text file created")

if __name__ == "__main__":
    site_url = "https://www.carmudi.com.ph/used-cars/metro-manila/"
    
    browser = open_browser(site_url)
    
    try:
        # Scroll to the bottom to load more content
        scroll_to_bottom(browser)

        # Allow time for content to load after scrolling
        time.sleep(6)

        car_titles, car_prices = scrape_data(browser)
        write_to_file(car_titles, car_prices)
        

        # Database connection details
        db_connection = psycopg2.connect(
            host="localhost",
            database="car_data",
            user="postgres",
            password="tanish@13579"
        )

        # Create a cursor for interacting with the database
        cursor = db_connection.cursor()

        # Insert data into the PostgreSQL database
        for title, price in zip(car_titles, car_prices):
            cursor.execute("INSERT INTO car_data (title, price) VALUES (%s, %s)", (title, price))

        # Commit changes and close the cursor and connection
        db_connection.commit()
        cursor.close()
        db_connection.close()
    finally:
        close_browser(browser)