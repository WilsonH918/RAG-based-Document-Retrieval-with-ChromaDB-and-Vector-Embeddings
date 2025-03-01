from Helpers import *
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
openai_key = os.getenv("OPENAI_API_KEY")

## Query
query_text = input("Enter your query: ")
# query_text = "tell me something related to crypto"
query_vector = get_openai_embedding(query_text, openai_key)

## Get article as pandas df
df = get_article(topic = "TECHNOLOGY")

## Initialize the ChromaDB client with persistence
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "title_article_collection"
## delete old collection
delete_collection(chroma_client, collection_name)
## create new collection
collection = chroma_client.get_or_create_collection(name=collection_name)

## Input embedding, title and link to Chroma db
for index, row in df.iterrows():
    title = row['title']
    link = row['link']
    doc_id = row['id'] 

    ## Check if the document already exists in the collection
    existing_result = collection.get(where={'doc_id': {"$in": [doc_id]}})

    ## If the document doesn't exist, add it to the collection
    if len(existing_result.get('ids', [])) == 0:
        # print(f"\nProcessing document with id {doc_id} (DataFrame index {index})")
        title_vector = get_openai_embedding(title, openai_key)  ## Generate embedding for the title

        collection.upsert(
            ids=[str(doc_id)],
            documents=[title],             ## The document is the title
            metadatas=[{"link": link}],     ## Store the link as metadata
            embeddings=[title_vector]       ## The generated embedding
        )
        # print(f"Document with id {doc_id} successfully upserted.")

print("\nTitle and Link successfully added to Chroma DB.")

## Retrieve the most relevant result (top 1)
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5
)

## Extract and print all links
if results["ids"]:
    best_match = [meta for sublist in results["metadatas"] for meta in sublist]  # Flatten list of lists
    all_links = [match["link"] for match in best_match]  # Extract all links
    print("Relevant links:", all_links)
else:
    print("No relevant link found.")

### retrieve link from chroma db
all_chunks = [] 
for url in all_links:
    print(f"web scrapping url: {url}")
    article_text = scrape_website(url)
    if article_text:
        chunks = split_text(article_text)  # chunks is already a list
        all_chunks.extend(chunks)

## Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "article_info_collection"
## delete old collection
delete_collection(chroma_client, collection_name)
## create new collection
collection = chroma_client.get_or_create_collection(name=collection_name)

## Process and insert each chunk into ChromaDB
for chunk in all_chunks:
    chunk_id = generate_id(chunk)  # Generate a unique ID for each chunk
    chunk_embedding = get_openai_embedding(chunk, openai_key)  # Generate embedding

    collection.upsert(
        ids=[chunk_id],  
        documents=[chunk],  # Store the chunk of text
        embeddings=[chunk_embedding]  
    )

print("\nArticle successfully added to Chroma DB.")

### final answer!!
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5  
)

passage = "\n".join(results["documents"][0])
# print(passage)

answer =  generate_response(query_text, passage, openai_key)
print(answer.content)

