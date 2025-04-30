import sys
from pathlib import Path
import json
import os

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.scrapers.restaurant_scraper import RestaurantScraper
from src.data.knowledge_base import KnowledgeBase

def main():
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Example restaurant URLs (replace with actual URLs)
    restaurant_urls = [
        "https://www.zomato.com/restaurant1",
        "https://www.zomato.com/restaurant2",
        # Add more URLs here
    ]
    
    # Initialize scraper
    scraper = RestaurantScraper()
    
    # Scrape restaurant data
    print("Scraping restaurant data...")
    restaurants = scraper.scrape_restaurants(restaurant_urls)
    
    # Save raw data
    raw_data_path = data_dir / "restaurants.json"
    scraper.save_to_json(restaurants, str(raw_data_path))
    print(f"Saved raw data to {raw_data_path}")
    
    # Initialize and populate knowledge base
    print("Processing data into knowledge base...")
    knowledge_base = KnowledgeBase()
    knowledge_base.process_scraped_data(restaurants)
    knowledge_base.build_index()
    
    # Save knowledge base
    kb_path = data_dir / "knowledge_base"
    knowledge_base.save(str(kb_path))
    print(f"Saved knowledge base to {kb_path}")

if __name__ == "__main__":
    main() 