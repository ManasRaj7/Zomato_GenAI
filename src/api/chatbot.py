import streamlit as st
import requests
import json
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

class SimpleChatbot:
    def __init__(self):
        if not HUGGINGFACE_API_KEY:
            st.error("HUGGINGFACE_API_KEY not found in .env file. Please add your Hugging Face API key to the .env file.")
            st.stop()
            
    def _call_huggingface_api(self, prompt: str):
        """Make API call to Hugging Face models."""
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Format prompt for Mistral
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.1,
                "top_p": 0.95,
                "do_sample": False,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(f"{HUGGINGFACE_API_URL}{MODEL_NAME}", headers=headers, json=payload)
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    if isinstance(response_json, list) and len(response_json) > 0:
                        generated_text = response_json[0].get("generated_text", "").strip()
                        if "Assistant:" in generated_text:
                            generated_text = generated_text.split("Assistant:", 1)[1].strip()
                        return generated_text
                    return "Error: Unexpected API response format"
                except json.JSONDecodeError:
                    return "Error: Invalid JSON response from API"
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                print(error_msg)
                return error_msg
        except requests.exceptions.RequestException as e:
            return f"Error: Could not connect to the API. Please check your internet connection. Details: {str(e)}"
        
    def get_response(self, query, context):
        """Get response from the model."""
        prompt = f"""You are a helpful restaurant assistant. Use this restaurant information to answer the question in a friendly, conversational way. Format your response nicely with bullet points or sections where appropriate.

Restaurant Data:
{context}

Question: {query}

Please provide a well-formatted, conversational response that directly answers the question using the restaurant information provided. If the information is not available, say so politely."""
        
        return self._call_huggingface_api(prompt)

def main():
    # Set page config
    st.set_page_config(
        page_title="Restaurant Assistant",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for dark theme
    st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stTextInput>div>div>input {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        .stTextInput>div>div>input::placeholder {
            color: #AAAAAA;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .chat-message.user {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        .chat-message.assistant {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
        }
        .stMarkdown {
            color: #FFFFFF;
        }
        .stTitle {
            color: #FFFFFF;
        }
        .stSpinner>div {
            background-color: #4CAF50;
        }
        .css-1d391kg {
            background-color: #2D2D2D;
        }
        .css-1d391kg:hover {
            background-color: #3D3D3D;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and description
    st.title("🍽️ Restaurant Assistant")
    st.markdown("""
        <div style='color: #AAAAAA; font-size: 1.1em;'>
            Ask me anything about restaurants, menus, and dining options in Bangalore!<br>
            I can help you find vegetarian, non-vegetarian, and other special dietary options.
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot
    chatbot = SimpleChatbot()
    
    # Load restaurant data
    data_file = Path("data/restaurants.json")
    if not data_file.exists():
        st.error("No restaurant data found. Please run the scraper first.")
        st.stop()
        
    try:
        with open(data_file) as f:
            restaurants = json.load(f)
    except json.JSONDecodeError:
        st.error("Error reading restaurant data. The file might be corrupted.")
        st.stop()
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about restaurants (e.g., 'What are the vegetarian options?', 'Which restaurants serve seafood?')"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Get context from restaurant data
        context = json.dumps(restaurants, indent=2)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.get_response(prompt, context)
                st.markdown(response)
                
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
