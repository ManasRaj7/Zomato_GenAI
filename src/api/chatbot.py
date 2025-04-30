import streamlit as st
import json
from typing import List, Dict, Any
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.models.rag_model import RAGModel
from src.data.knowledge_base import KnowledgeBase
from src.scripts.pipeline import RestaurantPipeline

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("HUGGINGFACE_API_KEY"):
    st.error("HUGGINGFACE_API_KEY not found in environment variables. Please add it to your .env file.")
    st.stop()

def load_restaurant_data():
    """Load restaurant data from JSON file."""
    try:
        with open("data/restaurants.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Restaurant data file not found. Please ensure data/restaurants.json exists.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error parsing restaurant data file. Please check the JSON format.")
        st.stop()

def initialize_rag():
    """Initialize the RAG system."""
    try:
        # Load restaurant data
        restaurant_data = load_restaurant_data()
        
        # Initialize knowledge base
        knowledge_base = KnowledgeBase()
        knowledge_base.add_documents(restaurant_data)
        
        # Initialize RAG model
        rag_model = RAGModel(knowledge_base)
        
        return rag_model
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        st.stop()

class RestaurantChatbot:
    def __init__(self, rag_model: RAGModel):
        """Initialize the chatbot with a RAG model."""
        self.rag_model = rag_model
        self.conversation_history = []
        
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context for display."""
        formatted = "Relevant Information:\n\n"
        for item in context:
            formatted += f"- {item['text']}\n"
            if 'metadata' in item:
                formatted += f"  Source: {item['metadata'].get('restaurant', 'Unknown')}\n"
        return formatted
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query and return a response."""
        try:
            # Get response from RAG model
            result = self.rag_model.handle_query(query)
            
            # Add to conversation history
            self.conversation_history.append({
                "query": query,
                "response": result["response"],
                "context": result["context"]
            })
            
            return result
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your query. Please try again.",
                "context": [],
                "status": "error"
            }
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history

def create_streamlit_app(chatbot: RestaurantChatbot):
    """Create a Streamlit interface for the chatbot."""
    st.title("Restaurant Information Assistant")
    st.write("Ask me anything about restaurants, menus, and dining options!")
    
    # Initialize session state for conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "context" in message and message["context"]:
                with st.expander("View Sources"):
                    st.write(chatbot._format_context(message["context"]))
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = chatbot.process_query(prompt)
                
                # Display response
                st.write(result["response"])
                
                # Display context in expander
                if result["context"]:
                    with st.expander("View Sources"):
                        st.write(chatbot._format_context(result["context"]))
                        
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "context": result["context"]
                })
                
    # Add sidebar with information
    with st.sidebar:
        st.header("About")
        st.write("""
        This chatbot can help you with:
        - Menu item availability and details
        - Restaurant feature comparisons
        - Price range inquiries
        - Dietary restriction questions
        - Restaurant reviews and ratings
        """)
        
        # Add example queries
        st.header("Example Queries")
        example_queries = [
            "Which restaurant has the best vegetarian options?",
            "What's the price range for desserts at Capella?",
            "Compare the spice levels in different restaurants",
            "Which restaurants offer gluten-free options?",
            "What are the most popular dishes at each restaurant?",
            "Which restaurant has the best reviews for Indian cuisine?"
        ]
        
        for query in example_queries:
            if st.button(query):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()

def main():
    """Main function to run the Streamlit app."""
    # Initialize pipeline
    pipeline = RestaurantPipeline()
    
    # Try to load existing data
    if not pipeline.load_existing_data():
        # If no existing data, create sample data and set up the pipeline
        pipeline.run_pipeline([])  # Empty list since we're using sample data
    
    # Ensure RAG model is set up
    if not pipeline.rag_model:
        pipeline.setup_rag_model()
    
    # Create chatbot with the pipeline's RAG model
    chatbot = RestaurantChatbot(pipeline.rag_model)
    
    # Create Streamlit app
    create_streamlit_app(chatbot)

if __name__ == "__main__":
    main()
