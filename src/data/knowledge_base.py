import json
from typing import List, Dict, Any
from pathlib import Path

class KnowledgeBase:
    def __init__(self):
        """Initialize the knowledge base."""
        self.documents = []
        self.metadata = []
        
    def process_scraped_data(self, data: List[Dict[str, Any]]) -> None:
        """Process scraped restaurant data into searchable format."""
        processed_docs = []
        processed_metadata = []
        
        for restaurant in data:
            # Create document chunks for each restaurant
            restaurant_info = self._create_restaurant_chunks(restaurant)
            processed_docs.extend(restaurant_info["chunks"])
            processed_metadata.extend(restaurant_info["metadata"])
            
        self.documents = processed_docs
        self.metadata = processed_metadata
        
    def _create_restaurant_chunks(self, restaurant: Dict[str, Any]) -> Dict[str, List]:
        """Create searchable chunks from restaurant data."""
        chunks = []
        metadata = []
        
        # Basic info chunk
        basic_info = f"Restaurant: {restaurant.get('restaurant_name', 'Unknown')}\n"
        basic_info += f"Location: {restaurant.get('location', 'Unknown')}\n"
        basic_info += f"Operating Hours: {restaurant.get('operating_hours', 'Unknown')}\n"
        basic_info += f"Rating: {restaurant.get('rating', 'Unknown')}\n"
        basic_info += f"Price Range: {restaurant.get('price_range', 'Unknown')}\n"
        chunks.append(basic_info)
        metadata.append({
            "type": "basic_info",
            "restaurant": restaurant.get('restaurant_name', 'Unknown')
        })
        
        # Menu items chunk
        if restaurant.get('menu_items'):
            menu_text = "Menu Items:\n"
            for item in restaurant['menu_items']:
                menu_text += f"- {item.get('name', 'Unknown')}: "
                if item.get('description'):
                    menu_text += f"{item['description']} "
                if item.get('price'):
                    menu_text += f"Price: {item['price']}\n"
            chunks.append(menu_text)
            metadata.append({
                "type": "menu",
                "restaurant": restaurant.get('restaurant_name', 'Unknown')
            })
        
        # Features chunk
        if restaurant.get('features'):
            features_text = f"Features for {restaurant.get('restaurant_name', 'Unknown')}:\n"
            for key, value in restaurant['features'].items():
                if isinstance(value, list):
                    features_text += f"{key}: {', '.join(value)}\n"
                else:
                    features_text += f"{key}: {value}\n"
            chunks.append(features_text)
            metadata.append({
                "type": "features",
                "restaurant": restaurant.get('restaurant_name', 'Unknown')
            })
            
        # Reviews chunk
        if restaurant.get('reviews'):
            reviews_text = f"Reviews for {restaurant.get('restaurant_name', 'Unknown')}:\n"
            for review in restaurant['reviews'][:5]:  # Limit to top 5 reviews
                reviews_text += f"Rating: {review.get('rating', 'Unknown')}\n"
                reviews_text += f"Comment: {review.get('comment', 'No comment')}\n"
                reviews_text += f"User: {review.get('user', 'Anonymous')}\n\n"
            chunks.append(reviews_text)
            metadata.append({
                "type": "reviews",
                "restaurant": restaurant.get('restaurant_name', 'Unknown')
            })
            
        return {"chunks": chunks, "metadata": metadata}
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Simple keyword-based search."""
        if not self.documents:
            raise ValueError("No documents to search. Process data first.")
        
        # Convert query to lowercase for case-insensitive search
        query = query.lower()
        
        # Score documents based on keyword matches
        scores = []
        for doc in self.documents:
            # Count how many query words appear in the document
            score = sum(1 for word in query.split() if word in doc.lower())
            scores.append(score)
        
        # Get top k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with some match
                results.append({
                    "text": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": scores[idx]
                })
        
        return results
    
    def save(self, path: str) -> None:
        """Save the knowledge base to disk."""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save documents and metadata
        with open(save_path / "documents.json", "w") as f:
            json.dump(self.documents, f)
        with open(save_path / "metadata.json", "w") as f:
            json.dump(self.metadata, f)
            
    def load(self, path: str) -> None:
        """Load the knowledge base from disk."""
        load_path = Path(path)
        
        # Load documents and metadata
        with open(load_path / "documents.json", "r") as f:
            self.documents = json.load(f)
        with open(load_path / "metadata.json", "r") as f:
            self.metadata = json.load(f)
