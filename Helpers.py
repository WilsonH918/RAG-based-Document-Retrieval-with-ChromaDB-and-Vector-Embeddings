import requests
import pandas as pd
import hashlib

# Generate a consistent hash (ID) based on the link
def generate_id(link):
    return str(hashlib.sha256(link.encode('utf-8')).hexdigest())


def Get_Article():
    # Your code to fetch the articles and return the DataFrame
    url = "https://real-time-news-data.p.rapidapi.com/topic-news-by-section"
    querystring = {"topic":"TECHNOLOGY","section":"CAQiSkNCQVNNUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENJT0NBUWFDZ29JTDIwdk1ETnliSFFxQ2hJSUwyMHZNRE55YkhRb0FBKi4IACoqCAoiJENCQVNGUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENnQVABUAE","limit":"500","country":"GB","lang":"en"}

    headers = {
        "x-rapidapi-key": "68968cc231msha447505cfb19142p1ebbe2jsnb72182824786",
        "x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data_list = []
    for data in response.json()['data']:
        data_list.append({'title': data['title'], 'link': data['link'].strip()})

    df = pd.DataFrame(data_list)

    df = df[df['title'].str.strip().notnull() & df['link'].str.strip().notnull()]
    df = df[df['title'].str.strip() != '']
    df = df[df['link'].str.strip() != '']
    df['id'] = df['link'].apply(generate_id)

    return df


##################################################


import os
import chromadb
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from chromadb.utils import embedding_functions

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

# Function to generate embeddings
def get_openai_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    print("==== Generating embeddings... ====")
    return embedding



# Initialize the ChromaDB client with persistence
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "title_article_collection"

# delete before process
try:
    chroma_client.delete_collection(name=collection_name)
    print(f"Collection '{collection_name}' deleted successfully.")
except Exception as e:
    print(f"Error deleting collection: {e}")

collection = chroma_client.get_or_create_collection(name=collection_name)

# Get the DataFrame from your Get_Article() function
df = Get_Article()

# Delete documents by ids (if needed)
# Check if the collection exists before deleting

# Now, let's add only new rows or those that are not present in the collection yet
for index, row in df.iterrows():
    title = row['title']
    link = row['link']
    doc_id = row['id'] 

    # Check if the document already exists in the collection
    # Use collection.get to check if the doc_id exists
    existing_result = collection.get(where={'doc_id': {"$in": [doc_id]}})

    # If the document doesn't exist, add it to the collection
    if len(existing_result.get('ids', [])) == 0:
        print(f"\nProcessing document with id {doc_id} (DataFrame index {index})")
        title_vector = get_openai_embedding(title)  # Generate embedding for the title
        # print(title_vector)

        collection.upsert(
            ids=[str(doc_id)],
            documents=[title],             # The document is the title
            metadatas=[{"link": link}],     # Store the link as metadata
            embeddings=[title_vector]       # The generated embedding
        )
        print(f"Document with id {doc_id} successfully upserted.")

print("\nData successfully added to Chroma DB.")



##################################################


import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

# Function to generate embeddings for queries
def get_openai_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    return embedding

# Initialize ChromaDB client with persistence
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "title_article_collection"
collection = chroma_client.get_collection(name=collection_name)

# Query
query_text = "tell me something related to crypto"
query_vector = get_openai_embedding(query_text)

# Retrieve the most relevant result (top 1)
results = collection.query(
    query_embeddings=[query_vector],
    n_results=1
)

# Extract and print the link
if results["ids"]:
    best_match = results["metadatas"][0][0]  # First result, first metadata dict
    print("Best matching link:", best_match["link"])
else:
    print("No relevant link found.")


##################################################

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import openai
import textwrap
# Function to scrape content from a URL
def scrape_website(url):
    # Send GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for HTTP errors

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get all the text from paragraphs (<p>) and headings (<h1>, <h2>, etc.)
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # Combine the text from all these tags
    text = " ".join([para.get_text() for para in paragraphs])

    return text

# Function to chunk the text into smaller pieces with overlap
def chunk_text(text, chunk_size=500, overlap=50):
    # Use textwrap to break the text into chunks
    chunks = textwrap.wrap(text, chunk_size, overlap)
    return chunks

# Main function to process the link and generate embeddings
def process_link(url):
    # Step 1: Scrape the website content
    print(f"Scraping content from {url}...")
    website_text = scrape_website(url)

    # Step 2: Chunk the content into smaller pieces with overlap
    print("Chunking content...")
    chunks = chunk_text(website_text)

    # Step 3: Send each chunk to the OpenAI API for embedding
    embeddings = []
    for chunk in chunks:
        embedding = get_openai_embedding(chunk)
        embeddings.append(embedding)

    print(f"Processed {len(chunks)} chunks from the website.")
    return embeddings

# Example usage:
url = best_match["link"]
process_link(url)


