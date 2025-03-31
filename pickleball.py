import time
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config('configs/configs.yaml')

LOGIN_URL = config['LOGIN_URL']
BOOKING_URL = config['BOOKING_URL']
USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']

def scrape_booking_page():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)

        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(3)  
        
        driver.get(BOOKING_URL)
        time.sleep(3)
        
        full_html = driver.page_source
        soup = BeautifulSoup(full_html, 'html.parser')
        
        marker_rows = soup.find_all('tr', class_='bm-marker-row')
        event_rows = soup.find_all('tr', class_='bm-class-row')
        
        current_date = None
        
        for marker_row in marker_rows:
            date_element = marker_row.find('h2', {'aria-label': True})
            if date_element:
                current_date = date_element.get_text(strip=True)  
                
            for row in event_rows:
                event_name = row.find('span', {'aria-label': True, 'class': 'bm-event-description'}).text.strip()
                event_time = row.find('span', {'aria-label': True}).text.strip()
                event_location = row.find('div', {'class': 'location-block'}).text.strip()
                event_price = row.find('span', {'aria-label': True, 'class': 'bm-event-description'}).find_next('span').text.strip()
                spots_left = row.find('span', {'aria-label': True}).text.strip()
                
                if 'pickleball' in event_name.lower():
                    print(f"=== Pickleball Event ===")
                    print(f"Date: {current_date}") 
                    print(f"Event: {event_name}")
                    print(f"Time: {event_time}")
                    print(f"Location: {event_location}")
                    print(f"Price: {event_price}")
                    print(f"Spots Left: {spots_left}")
                    print('---' * 10)
                
    finally:
        driver.quit()

scrape_booking_page()
