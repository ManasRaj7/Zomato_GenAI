import sys
from pathlib import Path
import json
import os
import logging
from typing import List, Dict, Any

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.scrapers.restaurant_scraper import RestaurantScraper
from src.data.knowledge_base import KnowledgeBase
from src.models.rag_model import RAGModel

class RestaurantPipeline:
    def __init__(self):
        """Initialize the pipeline components."""
        self.setup_logging()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.scraper = RestaurantScraper()
        self.knowledge_base = KnowledgeBase()
        
        # Create sample data and set up knowledge base
        restaurants = self.create_sample_data()
        self.process_to_knowledge_base(restaurants)
        
        # Initialize RAG model with knowledge base
        self.rag_model = RAGModel(self.knowledge_base)
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pipeline.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def scrape_data(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape restaurant data from provided URLs."""
        self.logger.info("Starting data scraping...")
        try:
            restaurants = self.scraper.scrape_multiple_restaurants(urls, str(self.data_dir / "restaurants.json"))
            self.logger.info(f"Scraped data for {len(restaurants)} restaurants")
            return restaurants
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            raise
            
    def process_to_knowledge_base(self, restaurants: List[Dict[str, Any]]) -> None:
        """Process scraped data into knowledge base."""
        self.logger.info("Processing data into knowledge base...")
        try:
            self.knowledge_base.process_scraped_data(restaurants)
            self.knowledge_base.build_index()
            
            # Save knowledge base
            kb_path = self.data_dir / "knowledge_base"
            self.knowledge_base.save(str(kb_path))
            self.logger.info(f"Saved knowledge base to {kb_path}")
        except Exception as e:
            self.logger.error(f"Error processing knowledge base: {str(e)}")
            raise
            
    def setup_rag_model(self) -> None:
        """Setup RAG model with knowledge base."""
        self.logger.info("Setting up RAG model...")
        try:
            if not self.knowledge_base:
                raise ValueError("Knowledge base not initialized")
            self.rag_model = RAGModel(self.knowledge_base)
            self.logger.info("RAG model setup complete")
        except Exception as e:
            self.logger.error(f"Error setting up RAG model: {str(e)}")
            raise
            
    def load_existing_data(self) -> bool:
        """Load existing knowledge base if available."""
        kb_path = self.data_dir / "knowledge_base"
        if kb_path.exists():
            self.logger.info("Loading existing knowledge base...")
            try:
                self.knowledge_base.load(str(kb_path))
                self.setup_rag_model()
                return True
            except Exception as e:
                self.logger.error(f"Error loading knowledge base: {str(e)}")
                return False
        return False
        
    def create_sample_data(self) -> List[Dict[str, Any]]:
        """Create sample restaurant data for testing."""
        self.logger.info("Creating sample restaurant data...")
        
        sample_restaurants = [
            {
                "restaurant_name": "Vegan Hub Indiranagar",
                "location": "Indiranagar, Bangalore",
                "operating_hours": "11:00 AM - 11:00 PM",
                "rating": "4.5",
                "price_range": "₹₹",
                "menu_items": [
                    {
                        "name": "Vegan Burger",
                        "price": "₹250",
                        "description": "Plant-based patty with fresh vegetables"
                    },
                    {
                        "name": "Tofu Scramble",
                        "price": "₹200",
                        "description": "Scrambled tofu with herbs and spices"
                    }
                ],
                "features": {
                    "cuisines": ["Vegan", "International"],
                    "amenities": ["Outdoor Seating", "Takeaway"],
                    "dietary_options": ["Vegan", "Gluten-Free"]
                },
                "reviews": [
                    {
                        "rating": "5.0",
                        "comment": "Best vegan food in Bangalore!",
                        "user": "John D."
                    }
                ]
            },
            {
                "restaurant_name": "Vegan Hub Koramangala",
                "location": "Koramangala, Bangalore",
                "operating_hours": "10:00 AM - 10:00 PM",
                "rating": "4.3",
                "price_range": "₹₹",
                "menu_items": [
                    {
                        "name": "Vegan Pizza",
                        "price": "₹300",
                        "description": "Plant-based cheese and fresh toppings"
                    },
                    {
                        "name": "Quinoa Bowl",
                        "price": "₹280",
                        "description": "Protein-rich quinoa with vegetables"
                    }
                ],
                "features": {
                    "cuisines": ["Vegan", "Italian"],
                    "amenities": ["Indoor Seating", "Delivery"],
                    "dietary_options": ["Vegan", "Nut-Free"]
                },
                "reviews": [
                    {
                        "rating": "4.5",
                        "comment": "Great vegan options!",
                        "user": "Sarah M."
                    }
                ]
            }
        ]
        
        # Save sample data
        raw_data_path = self.data_dir / "restaurants.json"
        with open(raw_data_path, 'w') as f:
            json.dump(sample_restaurants, f, indent=2)
        self.logger.info(f"Saved sample data to {raw_data_path}")
        
        return sample_restaurants
        
    def run_pipeline(self, urls: List[str], force_rescrape: bool = False) -> None:
        """Run the complete pipeline."""
        # Try to load existing data first
        if not force_rescrape and self.load_existing_data():
            self.logger.info("Using existing knowledge base")
            return
            
        # Create sample data instead of scraping
        restaurants = self.create_sample_data()
        self.process_to_knowledge_base(restaurants)
        self.setup_rag_model()
        self.logger.info("Pipeline completed successfully")

def main():
    """Main function to run the pipeline."""
    # Real Zomato restaurant URLs for Bangalore
    restaurant_urls = [
        "https://www.zomato.com/bangalore/vegan-hub-indiranagar",
        "https://www.zomato.com/bangalore/vegan-hub-koramangala",
        "https://www.zomato.com/bangalore/vegan-hub-hsr-layout",
        "https://www.zomato.com/bangalore/vegan-hub-whitefield",
        "https://www.zomato.com/bangalore/vegan-hub-electronic-city"
    ]
    
    pipeline = RestaurantPipeline()
    pipeline.run_pipeline(restaurant_urls)

if __name__ == "__main__":
    main() 