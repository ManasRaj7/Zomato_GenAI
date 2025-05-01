# Restaurant Chatbot with RAG

A restaurant recommendation chatbot that uses Retrieval-Augmented Generation (RAG) to provide intelligent responses about restaurants, menus, and dining options.

## Features

- **Web Scraping**: Collects restaurant data from Zomato
- **Knowledge Base**: Stores and organizes restaurant information
- **RAG System**: Combines retrieval and generation for intelligent responses
- **Chat Interface**: User-friendly Streamlit web interface
- **Dark Theme**: Modern, easy-on-the-eyes UI

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Hugging Face API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/restaurant-chatbot.git
cd restaurant-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Hugging Face API key:
```
HUGGINGFACE_API_KEY=your_api_key_here
```

## Project Structure

```
restaurant-chatbot/
├── data/                  # Scraped restaurant data
├── src/
│   ├── api/              # API and web interface
│   │   └── chatbot.py    # Streamlit chat interface
│   ├── models/           # RAG model implementation
│   ├── scrapers/         # Web scraping utilities
│   └── scripts/          # Utility scripts
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Usage

1. Run the scraper to collect restaurant data:
```bash
python src/scrapers/restaurant_scraper.py
```

2. Start the Streamlit chat interface:
```bash
streamlit run src/api/chatbot.py
```

3. Open your browser and navigate to `http://localhost:8501`

## Example Queries

- "What are the vegetarian options available?"
- "Which restaurants serve seafood?"
- "Show me restaurants with good ratings"
- "What are the operating hours of [restaurant name]?"
- "Find restaurants with [cuisine type] food"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for the Mistral model
- [Streamlit](https://streamlit.io/) for the web interface
- [Zomato](https://www.zomato.com/) for restaurant data
