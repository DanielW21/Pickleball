from scraper.search import EventScraper
from scraper._funcs import load_config
from scraper.discord import DiscordNotifier
import time
import random

def main():    
    interested_event_codes = ["61463","61457","61470","61472","61401","61404","61407"]

    start_time = time.time()
    
    # Load configuration
    config = load_config()
    scraper = EventScraper(config)
    
    try: 
        # Set URL and scrape events
        sports_url = scraper.config["BOOKING_URL"]
        scraper.set_url(sports_url)
        _ = scraper.scrape_events(["pickleball"])

        # Get all events and filter available ones
        all_events = scraper.get_all_searched_events()
        available_events = []
    
        for idx, (event_code, event_details) in enumerate(all_events.items()):
            if event_code in interested_event_codes:
                if event_details["spots_left"] != "Full":
                    available_events.append(event_details)
                    print(f"\nEvent #{idx + 1}, {event_details['name']} has {event_details['spots_left']} spots left")
                else:
                    print(f"Event #{idx + 1}, {event_details['name']} {event_details['date']} ({event_code}) is Full")
        
        discord_notifier = DiscordNotifier(config)
        discord_notifier.send_notification(available_events)
        
    finally:
        scraper.close()
        
    end_time = time.time()
    print(f"\n✅ Scraping completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
