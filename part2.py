import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import os
import chromadb
import hashlib


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

def generate_id(text):
    return str(hashlib.md5(text.encode()).hexdigest())

url = "https://mybigplunge.com/tech-plunge/blockchain/why-are-blockchains-so-important-to-the-future-of-the-internet/"
article_text = scrape_website(url)
chunks = split_text(article_text)
print(chunks)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "article_info_collection"
collection = chroma_client.get_or_create_collection(name=collection_name)

# Process and insert each chunk into ChromaDB
for chunk in chunks:
    chunk_id = generate_id(chunk)  # Generate a unique ID for each chunk
    chunk_embedding = get_openai_embedding(chunk)  # Generate embedding

    collection.upsert(
        ids=[chunk_id],  
        documents=[chunk],  # Store the chunk of text
        embeddings=[chunk_embedding]  
    )

print("Chunks successfully added to ChromaDB.")

# Query ChromaDB
query_text = "tell me something related to crypto"
query_vector = get_openai_embedding(query_text)

results = collection.query(
    query_embeddings=[query_vector],
    n_results=5  
)

passage = "\n".join(results["documents"][0])
print(passage)


# Function to generate a response from OpenAI
def generate_response(question, passage):
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

query_text = "tell me something related to crypto"
answer =  generate_response(query_text, passage)
print(answer)