import time
from urllib.parse import urljoin

import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_config("configs/configs.yaml")

LOGIN_URL = config["LOGIN_URL"]
BOOKING_URL = config["BOOKING_URL"]
USERNAME = config["USERNAME"]
PASSWORD = config["PASSWORD"]


def scrape_booking_page():
    count = 0

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        driver.get(LOGIN_URL)
        time.sleep(2)
        base_url = driver.current_url.split("/Clients")[0]  
        
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(2)

        driver.get(BOOKING_URL)
        time.sleep(2)

        full_html = driver.page_source
        soup = BeautifulSoup(full_html, "html.parser")

        rows = soup.find_all("tr", class_=["bm-marker-row", "bm-class-row"])

        current_date = None

        for row in rows:
            if "bm-marker-row" in row.get("class", []):
                date_element = row.find("h2", {"aria-label": True})
                if date_element:
                    current_date = date_element.get_text(strip=True)
            elif "bm-class-row" in row.get("class", []):
                event_name_element = row.find(
                    "span",
                    {
                        "class": "bm-event-description",
                        "aria-label": lambda x: x and "event" in x,
                    },
                )
                if not event_name_element:
                    continue

                event_name = event_name_element.get_text(strip=True)

                if "pickleball" in event_name.lower():
                    # TODO: Implement a more robust way to get the event number

                    # Get event time
                    time_element = row.find(
                        "span", {"aria-label": lambda x: x and "time" in x.lower()}
                    )
                    event_time = (
                        time_element.get_text(strip=True) if time_element else "N/A"
                    )

                    # Get location
                    location_element = row.find("div", {"class": "location-block"})
                    event_location = (
                        location_element.get_text(strip=True)
                        if location_element
                        else "N/A"
                    )

                    # Get spots left
                    spots_element = row.find(
                        "span",
                        {"aria-label": lambda x: x and "spots left" in x.lower()},
                    )
                    spots_left = (
                        spots_element.get_text(strip=True) if spots_element else "N/A"
                    )

                    # Get booking link
                    booking_button = row.find("input", {"class": "bm-button"})
                    if booking_button and booking_button.get("onclick"):
                        relative_path = booking_button["onclick"].split("'")[1]
                        booking_link = urljoin(base_url, relative_path)
                    else:
                        booking_link = "N/A"

                    print("\n", count)
                    count += 1

                    print(f"=== Pickleball Event ===")
                    print(f"Date: {current_date}")
                    print(f"Event: {event_name}")
                    # print(f"Event Number: {event_number}")
                    print(f"Time: {event_time}")
                    print(f"Location: {event_location}")
                    print(f"Spots Left: {spots_left}")
                    print(f"Booking Link: {booking_link}")
                    print("---" * 10)

    finally:
        driver.quit()


scrape_booking_page()
