from typing import List, Dict, Any
import requests
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.data.knowledge_base import KnowledgeBase

class RAGModel:
    def __init__(self, knowledge_base: KnowledgeBase):
        """Initialize RAG model with knowledge base."""
        self.knowledge_base = knowledge_base
        self.conversation_history = []
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _format_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Format the prompt with context and query."""
        # Format context
        context_str = "\n".join([
            f"Source {i+1}:\n{chunk['text']}\n"
            for i, chunk in enumerate(context)
        ])
        
        # Format conversation history
        history_str = ""
        if self.conversation_history:
            history_str = "Previous conversation:\n" + "\n".join([
                f"User: {msg['query']}\nAssistant: {msg['response']}\n"
                for msg in self.conversation_history[-3:]  # Last 3 exchanges
            ]) + "\n"
        
        # Construct the full prompt
        prompt = f"""You are a helpful restaurant information assistant. Use the following context to answer the user's question. If the answer cannot be found in the context, say so.

Context:
{context_str}

{history_str}User: {query}

Assistant:"""
        return prompt

    def _call_model(self, prompt: str) -> str:
        """Call the Hugging Face API."""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 500}}
            )
            response.raise_for_status()
            return response.json()[0]["generated_text"].split("Assistant:")[-1].strip()
        except Exception as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return "I apologize, but I'm having trouble generating a response at the moment."

    def query(self, query: str) -> Dict[str, Any]:
        """Process a query and return response with sources."""
        # Get relevant context
        context = self.knowledge_base.search(query)
        
        # Format prompt
        prompt = self._format_prompt(query, context)
        
        # Get response from model
        response = self._call_model(prompt)
        
        # Update conversation history
        self.conversation_history.append({
            "query": query,
            "response": response
        })
        
        # Format sources
        sources = [
            {
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            }
            for chunk in context
        ]
        
        return {
            "response": response,
            "sources": sources
        }
