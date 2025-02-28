import os
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "title_article_collection"

# Check if the collection exists before deleting
try:
    chroma_client.delete_collection(name=collection_name)
    print(f"Collection '{collection_name}' deleted successfully.")
except Exception as e:
    print(f"Error deleting collection: {e}")
    print('test')