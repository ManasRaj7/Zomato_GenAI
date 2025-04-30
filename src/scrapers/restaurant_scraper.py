import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Any
import logging
from pathlib import Path
import json
import re
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import sys

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

class RestaurantScraper:
    def __init__(self):
        """Initialize the scraper with necessary configurations."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.zomato.com"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed for the URL."""
        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = requests.get(robots_url, headers=self.headers)
            return "Disallow: /" not in response.text
        except Exception as e:
            self.logger.warning(f"Error checking robots.txt: {str(e)}")
            return False
            
    def scrape_restaurant(self, url: str) -> Dict[str, Any]:
        """Scrape a single restaurant's data."""
        if not self._check_robots_txt(url):
            self.logger.warning(f"Scraping not allowed for {url}")
            return None
            
        try:
            # Add random delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract restaurant information
            restaurant_data = {
                'restaurant_name': self._extract_restaurant_name(soup),
                'location': self._extract_location(soup),
                'operating_hours': self._extract_operating_hours(soup),
                'rating': self._extract_rating(soup),
                'price_range': self._extract_price_range(soup),
                'menu_items': self._extract_menu_items(soup),
                'features': self._extract_restaurant_features(soup),
                'reviews': self._extract_reviews(soup)
            }
            
            return restaurant_data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None
            
    def _extract_restaurant_name(self, soup: BeautifulSoup) -> str:
        """Extract restaurant name from the page."""
        # This is a placeholder - implement specific extraction logic for each website
        name = soup.find('h1', {'class': 'restaurant-name'})
        return name.text.strip() if name else "Unknown"
        
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract restaurant location from the page."""
        # This is a placeholder - implement specific extraction logic for each website
        location = soup.find('div', {'class': 'location'})
        return location.text.strip() if location else "Unknown"
        
    def _extract_operating_hours(self, soup: BeautifulSoup) -> str:
        """Extract operating hours from the page."""
        # This is a placeholder - implement specific extraction logic for each website
        hours = soup.find('div', {'class': 'operating-hours'})
        return hours.text.strip() if hours else "Unknown"
        
    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """Extract restaurant rating from the page."""
        # This is a placeholder - implement specific extraction logic for each website
        rating = soup.find('div', {'class': 'rating'})
        return rating.text.strip() if rating else "Unknown"
        
    def _extract_price_range(self, soup: BeautifulSoup) -> str:
        """Extract restaurant price range from the page."""
        # This is a placeholder - implement specific extraction logic for each website
        price_range = soup.find('div', {'class': 'price-range'})
        return price_range.text.strip() if price_range else "Unknown"
        
    def _extract_menu_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract menu items from the restaurant page."""
        menu_items = []
        menu_section = soup.find('div', {'class': 'menu-section'})
        
        if menu_section:
            for item in menu_section.find_all('div', {'class': 'menu-item'}):
                name = item.find('h4', {'class': 'item-name'})
                price = item.find('span', {'class': 'item-price'})
                description = item.find('p', {'class': 'item-description'})
                
                menu_items.append({
                    'name': name.text.strip() if name else 'Unknown',
                    'price': price.text.strip() if price else 'Price not available',
                    'description': description.text.strip() if description else 'No description available'
                })
                
        return menu_items
        
    def _extract_restaurant_features(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract restaurant features and amenities."""
        features = {}
        
        # Extract cuisine types
        cuisine_section = soup.find('div', {'class': 'cuisine-section'})
        if cuisine_section:
            features['cuisines'] = [c.text.strip() for c in cuisine_section.find_all('span')]
            
        # Extract amenities
        amenities_section = soup.find('div', {'class': 'amenities-section'})
        if amenities_section:
            features['amenities'] = [a.text.strip() for a in amenities_section.find_all('li')]
            
        # Extract dietary options
        dietary_section = soup.find('div', {'class': 'dietary-options'})
        if dietary_section:
            features['dietary_options'] = [d.text.strip() for d in dietary_section.find_all('span')]
            
        return features
        
    def _extract_reviews(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract restaurant reviews."""
        reviews = []
        review_section = soup.find('div', {'class': 'reviews-section'})
        
        if review_section:
            for review in review_section.find_all('div', {'class': 'review-card'}):
                rating = review.find('div', {'class': 'rating'})
                comment = review.find('div', {'class': 'comment'})
                user = review.find('div', {'class': 'user-name'})
                
                reviews.append({
                    'rating': rating.text.strip() if rating else 'No rating',
                    'comment': comment.text.strip() if comment else 'No comment',
                    'user': user.text.strip() if user else 'Anonymous'
                })
                
        return reviews
        
    def save_data(self, data: List[Dict[str, Any]], output_path: str):
        """Save scraped data to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def scrape_multiple_restaurants(self, urls: List[str], output_path: str):
        """Scrape multiple restaurants and save the data."""
        all_data = []
        
        for url in urls:
            self.logger.info(f"Scraping {url}")
            restaurant_data = self.scrape_restaurant(url)
            if restaurant_data:
                all_data.append(restaurant_data)
                
        self.save_data(all_data, output_path)
        return all_data 