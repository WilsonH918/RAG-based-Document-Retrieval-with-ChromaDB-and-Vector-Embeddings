import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
from chromadb.utils import embedding_functions

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key, model_name="text-embedding-ada-002"  # Ensure you use a matching model here
)

print(openai_ef)

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")

# Access or create the collection
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(
    name=collection_name, embedding_function=openai_ef
)

# Query the collection
results = collection.query(query_texts="tell me about databricks", n_results=2)

# Print the results
print(results)
