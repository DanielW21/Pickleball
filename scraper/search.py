from urllib.parse import urljoin
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scraper._funcs import load_config

class EventScraper:
    def __init__(self, config):
        """Initialize the scraper with configuration"""
        self.config = config
        self.BOOKING_URL = self.config["BOOKING_URL"]
        self.BASE_URL = urljoin(self.BOOKING_URL, "/")
        self.searched_events = {}  # Dictionary to store all events by their 5-digit code
        self.driver = None
    
    def set_url(self, new_url):
        """Update the booking URL and base URL"""
        self.BOOKING_URL = new_url
        self.BASE_URL = urljoin(self.BOOKING_URL, "/")
        self.searched_events = {}  # Clear previous events when URL changes
    
    def _initialize_driver(self):
        """Initialize the Selenium WebDriver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
    
    def _scrape_page(self):
        """Scrape the booking page and return all events"""
        self.driver.get(self.BOOKING_URL)
        
        # Wait until at least one event row is present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr.bm-class-row"))
        )
        
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        rows = soup.find_all("tr", class_=["bm-marker-row", "bm-class-row"])
        return rows
    
    def _parse_event_row(self, row, current_date):
        """Parse a single event row and return event data"""
        # Find the event name element
        event_name_element = row.find(
            "span", 
            class_="bm-event-description", 
            attrs={"aria-label": lambda x: x and "event" in x and "spots left" not in x}
        )
        if not event_name_element:
            return None
        
        event_name = event_name_element.get_text(strip=True)
        
        # Find the event code (extract just the digits)
        event_code_element = row.find(
            "span", 
            class_="bm-event-description", 
            attrs={"aria-label": lambda x: x and x.endswith("event") and x != event_name_element.get("aria-label", "")}
        )
        event_code = "".join(filter(str.isdigit, event_code_element.get_text(strip=True))) if event_code_element else "N/A"
        
        # Extract event details
        event_time = row.find("span", {"aria-label": lambda x: x and "time" in x.lower()})
        event_time = event_time.get_text(strip=True) if event_time else "N/A"

        event_location = row.find("div", class_="location-block")
        event_location = event_location.get_text(strip=True) if event_location else "N/A"

        spots_left = row.find("span", {"aria-label": lambda x: x and "spots left" in x.lower()})
        spots_left = spots_left.get_text(strip=True) if spots_left else "N/A"

        # Extract booking link
        booking_button = row.find("input", class_="bm-button")
        booking_link = "N/A"
        if booking_button and booking_button.get("onclick"):
            onclick_text = booking_button["onclick"]
            if "'" in onclick_text:
                relative_path = onclick_text.split("'")[1]
                booking_link = urljoin(self.BASE_URL, relative_path)
        
        return {
            "code": event_code,
            "date": current_date,
            "time": event_time,
            "name": event_name,
            "location": event_location,
            "spots_left": spots_left,
            "booking_link": booking_link
        }
    
    def scrape_events(self, event_names):
        """
        Scrape events matching the given names (can be string or list) 
        and store results. Returns dictionary of {event_type: [events]}
        """
        if isinstance(event_names, str):
            event_names = [event_names]
            
        event_names = [name.lower() for name in event_names]
        results = {name: [] for name in event_names}
        
        try:
            if not self.driver:
                self._initialize_driver()
            
            rows = self._scrape_page()
            current_date = None
            
            for row in rows:
                if "bm-marker-row" in row.get("class", []):
                    date_element = row.find("h2", {"aria-label": True})
                    if date_element:
                        current_date = date_element.get_text(strip=True)
                elif "bm-class-row" in row.get("class", []):
                    event_data = self._parse_event_row(row, current_date)
                    if event_data:
                        # Check against all event names we're searching for
                        for name in event_names:
                            if name in event_data["name"].lower():
                                # Store event with code as key
                                if event_data["code"] != "N/A":
                                    self.searched_events[event_data["code"]] = {
                                        "date": event_data["date"],
                                        "time": event_data["time"],
                                        "name": event_data["name"],
                                        "location": event_data["location"],
                                        "spots_left": event_data["spots_left"],
                                        "booking_link": event_data["booking_link"],
                                        "type": name  # Track which event type matched
                                    }
                                
                                else:
                                    print("Failed to add: ", event_data["name"])
                                    
                                results[name].append(event_data)
                                break  # No need to check other names once matched
                
            return results
            
        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            return {name: [] for name in event_names}
    
    def get_all_searched_events(self):
        """Return all events that have been searched for, keyed by 5-digit code"""
        return self.searched_events
    
    def get_events_by_type(self, event_type):
        """Get all events of a specific type"""
        return [event for event in self.searched_events.values() 
                if event.get("type") == event_type.lower()]
    
    def get_event_by_code(self, event_code):
        """Get a specific event by its 5-digit code"""
        return self.searched_events.get(event_code)
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


if __name__ == "__main__":
    scraper = EventScraper()  # Initialize with default config
    
    try:
        # First URL - Sports page
        sports_url = scraper.config["BOOKING_URL"]
        scraper.set_url(sports_url)
        sports_results = scraper.scrape_events(["pickleball", "badminton"])
        
        print("\n🏀 Sports Events:")
        for event_type, events in sports_results.items():
            print(f"\nFound {len(events)} {event_type} events:")
            for event in events:
                print(f"  {event['date']} {event['time']}: {event['name']}")
        
        # Second URL - Fitness page
        fitness_url = scraper.config["FITNESS_URL"]
        scraper.set_url(fitness_url)
        fitness_results = scraper.scrape_events(["yoga", "zumba"])
        
        print("\n💪 Fitness Events:")
        for event_type, events in fitness_results.items():
            print(f"\nFound {len(events)} {event_type} events:")
            for event in events:
                print(f"  {event['date']} {event['time']}: {event['name']}")

        #NOTE: You can still access combined events based on event name through:
        # all_events = scraper.get_all_searched_events()
                
    finally:
        scraper.close()