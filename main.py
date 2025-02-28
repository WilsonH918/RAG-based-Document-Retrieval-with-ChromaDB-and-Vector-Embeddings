import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import os

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

# Function to split the text into chunks with overlap
def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap  # Overlap the previous chunk
    return chunks

# Main function to process the link and generate embeddings
def process_link(url):
    # Step 1: Scrape the website content
    print(f"Scraping content from {url}...")
    website_text = scrape_website(url)

    # Step 2: Split the content into smaller pieces with overlap
    print("Splitting content into chunks...")
    chunks = split_text(website_text)

    # Step 3: Send each chunk to the OpenAI API for embedding
    embeddings = []
    for chunk in chunks:
        embedding = get_openai_embedding(chunk)
        embeddings.append(embedding)

    print(f"Processed {len(chunks)} chunks from the website.")
    return embeddings

# Example usage:
url = "https://crypto.news/study-the-current-bitcoin-adoption-level-is-like-the-internet-in-1990/"
embeddings = process_link(url)


