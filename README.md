# ChromaQuery: AI-Powered Knowledge Retrieval

## Overview
ChromaQuery is an AI-powered knowledge retrieval system that integrates retrieval-augmented generation (RAG), web scraping, and ChromaDB for accurate and real-time responses. The system uses OpenAI embeddings and vector search to retrieve relevant articles and generate contextual answers.

The project consists of three parts:  
- RAG (Retrieval-Augmented Generation): Combines document retrieval and language generation to enhance response accuracy using OpenAI embeddings and vector-based search.
- Web Scraping: Extracts and updates content from online sources using BeautifulSoup and requests.
- ChromaDB: Stores and indexes documents and their embeddings for efficient retrieval using semantic search.

## Project Architecture
[ User Input ]
      ↓
[ Generate Query Embedding ] → [ ChromaDB - Store Embeddings and Metadata ]
      ↓
[ Web Scraping of Articles ]
      ↓
[ Store Article Chunks in ChromaDB ]
      ↓
[ Retrieve Relevant Chunks ]
      ↓
[ Generate AI-Generated Response ]

