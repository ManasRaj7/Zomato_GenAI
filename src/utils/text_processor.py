import re
from typing import List, Dict, Any
import html2text
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove HTML tags
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text.strip()

def extract_restaurant_info(html_content: str) -> Dict[str, Any]:
    """Extract structured restaurant information from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize restaurant info dictionary
    restaurant_info = {
        "restaurant_name": None,
        "location": None,
        "menu_items": [],
        "special_features": None,
        "operating_hours": None,
        "contact_info": {}
    }
    
    # Extract basic information
    name_elem = soup.find('h1', class_='sc-1q7bklc-1')
    if name_elem:
        restaurant_info["restaurant_name"] = clean_text(name_elem.text)
        
    location_elem = soup.find('p', class_='sc-1hez2tp-0')
    if location_elem:
        restaurant_info["location"] = clean_text(location_elem.text)
        
    # Extract menu items
    menu_items = soup.find_all('div', class_='sc-1q7bklc-2')
    for item in menu_items:
        menu_item = {
            "name": None,
            "description": None,
            "price": None
        }
        
        name_elem = item.find('h4')
        if name_elem:
            menu_item["name"] = clean_text(name_elem.text)
            
        desc_elem = item.find('p', class_='sc-1hez2tp-0')
        if desc_elem:
            menu_item["description"] = clean_text(desc_elem.text)
            
        price_elem = item.find('span', class_='sc-1hez2tp-0')
        if price_elem:
            menu_item["price"] = clean_text(price_elem.text)
            
        restaurant_info["menu_items"].append(menu_item)
        
    # Extract special features
    features_elem = soup.find('div', class_='sc-1hez2tp-0')
    if features_elem:
        restaurant_info["special_features"] = clean_text(features_elem.text)
        
    # Extract operating hours
    hours_elem = soup.find('div', class_='sc-1hez2tp-0')
    if hours_elem:
        restaurant_info["operating_hours"] = clean_text(hours_elem.text)
        
    # Extract contact information
    contact_info = {}
    phone_elem = soup.find('a', href=re.compile(r'tel:'))
    if phone_elem:
        contact_info["phone"] = clean_text(phone_elem.text)
        
    email_elem = soup.find('a', href=re.compile(r'mailto:'))
    if email_elem:
        contact_info["email"] = clean_text(email_elem.text)
        
    restaurant_info["contact_info"] = contact_info
    
    return restaurant_info

def normalize_price(price_str: str) -> float:
    """Normalize price string to float value."""
    if not price_str:
        return None
        
    # Extract numeric value
    price_match = re.search(r'₹\s*([\d,]+)', price_str)
    if price_match:
        price = float(price_match.group(1).replace(',', ''))
        return price
    return None

def extract_dietary_info(text: str) -> List[str]:
    """Extract dietary information from text."""
    dietary_keywords = {
        "vegetarian": ["vegetarian", "veg"],
        "vegan": ["vegan"],
        "gluten-free": ["gluten-free", "gluten free"],
        "spicy": ["spicy", "hot"],
        "halal": ["halal"],
        "kosher": ["kosher"]
    }
    
    found_info = []
    text_lower = text.lower()
    
    for category, keywords in dietary_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            found_info.append(category)
            
    return found_info
