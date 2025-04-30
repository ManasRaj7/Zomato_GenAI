# Restaurant Recommendation Chatbot

This is a Streamlit-based chatbot application that provides restaurant recommendations based on user queries. The chatbot uses a RAG (Retrieval-Augmented Generation) model to provide accurate and context-aware responses.

## Features

- Interactive chat interface
- Restaurant recommendations based on user queries
- Context-aware responses using RAG model
- Support for various query types (cuisine, location, price range, etc.)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Hugging Face API key:
```
HUGGINGFACE_API_KEY=your_api_key_here
```

5. Ensure you have the restaurant data in the correct format at `data/restaurants.json`

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run src/api/chatbot.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Usage

1. Type your query in the chat input box
2. The chatbot will process your query and provide relevant restaurant recommendations
3. You can ask about:
   - Specific cuisines
   - Price ranges
   - Locations
   - Restaurant features
   - And more!

## Project Structure

```
.
├── data/
│   └── restaurants.json
├── src/
│   ├── api/
│   │   └── chatbot.py
│   ├── models/
│   │   ├── knowledge_base.py
│   │   └── rag_model.py
│   └── utils/
│       └── text_processor.py
├── .env
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
