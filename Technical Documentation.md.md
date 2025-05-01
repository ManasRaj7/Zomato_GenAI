**Technical Documentation (Zomato Gen AI Internship Assignment
solution)**

**Technical Documentation** in **Markdown format** for the given
RAGModel code.

**RAGModel Technical Documentation**

**Table of Contents**

1.  [System
    Architecture](https://chatgpt.com/c/681401ef-f990-8005-936a-fde9b6360801#system-architecture)

2.  [Implementation Details and Design
    Decisions](https://chatgpt.com/c/681401ef-f990-8005-936a-fde9b6360801#implementation-details-and-design-decisions)

3.  [Challenges Faced and Solutions
    Implemented](https://chatgpt.com/c/681401ef-f990-8005-936a-fde9b6360801#challenges-faced-and-solutions-implemented)

4.  [Future Improvement
    Opportunities](https://chatgpt.com/c/681401ef-f990-8005-936a-fde9b6360801#future-improvement-opportunities)

**System Architecture**

**Overview**

The RAGModel (Retrieval-Augmented Generation Model) is a system designed
to answer user queries using a combination of:

- A **Knowledge Base** for context retrieval.

- A **Large Language Model** (LLM) via Hugging Face API
  (Mistral-7B-Instruct-v0.2).

- Optional **conversation memory** for multi-turn interactions.

**Components**

User Query

\|

v

KnowledgeBase.search(query) \-\-\-\--\> Retrieve Top-K Chunks

\|

v

Format prompt with context and conversation history

\|

v

Send formatted prompt to HuggingFace Inference API

\|

v

Parse and return response + context sources

- **KnowledgeBase**: Handles semantic search using vector embeddings
  (assumed to be pre-implemented).

- **Mistral-7B LLM**: Performs language generation based on the prompt.

- **Conversation Memory**: Maintains the last 3 user-assistant exchanges
  to simulate ongoing conversation.

**Implementation Details and Design Decisions**

**Code Modules and Classes**

- **RAGModel**

  - \_\_init\_\_: Loads environment variables, sets API parameters,
    initializes history.

  - \_format_prompt: Formats the full prompt combining context and past
    interactions.

  - \_call_model: Sends the prompt to the Hugging Face API and parses
    the response.

  - query: Main interface to process user queries and return model
    response with sources.

**Design Decisions**

1.  **Stateless API Call**: Uses HTTP POST requests to HuggingFace's
    hosted model instead of running a local LLM, simplifying deployment.

2.  **Limited Conversation History**: Only the last 3 exchanges are
    stored to reduce prompt length while maintaining coherence.

3.  **Dotenv for Secrets**: Uses python-dotenv to securely manage the
    Hugging Face API key.

4.  **Context Injection**: The prompt embeds top context chunks with
    identifiers (Source 1, 2, \...) for traceability.

**Challenges Faced and Solutions Implemented**

**1. Token Limit Management**

- **Challenge**: Hugging Face models have a maximum input size.

- **Solution**: Limit the context to top N results (not shown in code
  but assumed in KnowledgeBase.search) and truncate conversation history
  to the last 3 exchanges.

**2. Error Handling for API Calls**

- **Challenge**: API calls may fail due to network issues or rate
  limits.

- **Solution**: Wrapped the request in a try-except block with graceful
  fallback message.

**3. Prompt Engineering**

- **Challenge**: Prompt must be effective yet concise to elicit relevant
  answers.

- **Solution**: Structured prompt with consistent formatting, roles
  (User/Assistant), and instructions to the model.

**Future Improvement Opportunities**

1.  **Streaming Responses**  
    Use streaming models or WebSockets to deliver partial results in
    real-time for improved UX.

2.  **Token Budgeting Logic**  
    Dynamically adjust the number of retrieved chunks or truncate text
    based on remaining token budget.

3.  **Feedback Loop Integration**  
    Allow user feedback on accuracy of responses to fine-tune retrieval
    or improve ranking.

4.  **Caching Layer**  
    Store model outputs for repeated queries to reduce latency and cost.

5.  **Metadata-Aware Retrieval**  
    Enhance the KnowledgeBase to rank results using metadata relevance,
    not just semantic similarity.

6.  **Switch to Open-Source LLM (optional)**  
    For cost-saving or data privacy, integrate local LLMs (e.g., Mistral
    via HuggingFace Transformers + ONNX).
