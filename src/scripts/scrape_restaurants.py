import sys
from pathlib import Path

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.scrapers.restaurant_scraper import RestaurantScraper

def main():
    # Initialize scraper
    scraper = RestaurantScraper()
    
    # List of restaurant URLs to scrape
    restaurant_urls = [
        # Add your restaurant URLs here
        # Example: "https://www.restaurant1.com",
        # Example: "https://www.restaurant2.com",
    ]
    
    if not restaurant_urls:
        print("Please add restaurant URLs to scrape in the script.")
        return
    
    # Scrape restaurants and save data
    output_path = "data/restaurants.json"
    scraped_data = scraper.scrape_multiple_restaurants(restaurant_urls, output_path)
    
    print(f"Successfully scraped {len(scraped_data)} restaurants")
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main() 