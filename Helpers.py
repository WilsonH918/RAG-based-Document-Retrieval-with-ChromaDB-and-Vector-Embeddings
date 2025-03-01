import requests
import pandas as pd
import hashlib
import os
import chromadb
import pandas as pd
from dotenv import load_dotenv
from chromadb.utils import embedding_functions
from openai import OpenAI
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")
rapidapi_key = os.getenv("RAPID_API_KEY")


# Generate a consistent hash (ID) based on the link
def generate_id(link):
    return str(hashlib.sha256(link.encode('utf-8')).hexdigest())

def get_article(rapidapi_key, topic = "TECHNOLOGY"):
    # Your code to fetch the articles and return the DataFrame
    url = "https://real-time-news-data.p.rapidapi.com/topic-news-by-section"
    querystring = {"topic":topic,"section":"CAQiSkNCQVNNUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENJT0NBUWFDZ29JTDIwdk1ETnliSFFxQ2hJSUwyMHZNRE55YkhRb0FBKi4IACoqCAoiJENCQVNGUW9JTDIwdk1EZGpNWFlTQldWdUxVZENHZ0pKVENnQVABUAE","limit":"500","country":"GB","lang":"en"}

    headers = {
        "x-rapidapi-key": rapidapi_key,
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

# Function to generate embeddings
def get_openai_embedding(text, openai_key):
    client = OpenAI(api_key=openai_key)
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    print("====Generating embeddings====")
    return embedding

# delete chroma db collection
def delete_collection(chroma_client, collection_name):
    # Initialize the ChromaDB client with persistence
    chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")

    # delete before process
    try:
        chroma_client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting collection: {e}")

# Function to scrape content from a URL
def scrape_website(url):
    try:
        # Send GET request to the URL
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all the text from paragraphs (<p>) and headings (<h1>, <h2>, etc.)
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        # Combine the text from all these tags
        text = " ".join([para.get_text() for para in paragraphs])

        return text
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError for {url}: {e}, move on to next link...")
    except requests.exceptions.RequestException as e:
        print(f"RequestException for {url}: {e}, move on to next link...")
    
    return None

# Function to split the text into chunks with overlap
def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap  # Overlap the previous chunk
    return chunks

# Function to generate a response from OpenAI
def generate_response(question, passage, openai_key):
    client = OpenAI(api_key=openai_key)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use five sentences maximum and keep the answer concise."
        "\n\nContext:\n" + passage + "\n\nQuestion:\n" + question
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message
    return answer