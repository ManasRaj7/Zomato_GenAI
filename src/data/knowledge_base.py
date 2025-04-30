import json
import pandas as pd
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

class KnowledgeBase:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the knowledge base with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.index = None
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
        
        # Special features chunk
        if restaurant.get('special_features'):
            features_text = f"Special Features for {restaurant.get('restaurant_name', 'Unknown')}:\n"
            features_text += restaurant['special_features']
            chunks.append(features_text)
            metadata.append({
                "type": "features",
                "restaurant": restaurant.get('restaurant_name', 'Unknown')
            })
            
        return {"chunks": chunks, "metadata": metadata}
    
    def build_index(self) -> None:
        """Build FAISS index from processed documents."""
        if not self.documents:
            raise ValueError("No documents to index. Process data first.")
            
        # Generate embeddings
        embeddings = self.model.encode(self.documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information."""
        if not self.index:
            raise ValueError("Index not built. Call build_index() first.")
            
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Search the index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return results with metadata
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append({
                "text": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(1 / (1 + distance))  # Convert distance to similarity score
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
            
        # Save FAISS index
        if self.index:
            faiss.write_index(self.index, str(save_path / "index.faiss"))
            
    def load(self, path: str) -> None:
        """Load the knowledge base from disk."""
        load_path = Path(path)
        
        # Load documents and metadata
        with open(load_path / "documents.json", "r") as f:
            self.documents = json.load(f)
        with open(load_path / "metadata.json", "r") as f:
            self.metadata = json.load(f)
            
        # Load FAISS index
        index_path = load_path / "index.faiss"
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
