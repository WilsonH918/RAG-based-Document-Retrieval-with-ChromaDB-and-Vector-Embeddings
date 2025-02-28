import chromadb

# Initialize Chroma DB client with persistence
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "title_article_collection"
collection = chroma_client.get_collection(name=collection_name)

# Example IDs to delete (ensure these IDs exist in the collection)
ids_to_delete = ['-3812494819038408445', '8095615873978416859']

# Print out existing IDs before deletion
existing_result = collection.get()
existing_ids = set(existing_result.get("ids", []))
print("Existing IDs in collection:")
for doc_id in existing_ids:
    print(doc_id)

# Deleting specified IDs
collection.delete(ids=ids_to_delete)

# Re-check to ensure the IDs were deleted
existing_result_after_delete = collection.get()
existing_ids_after_delete = set(existing_result_after_delete.get("ids", []))

# Print out the IDs after deletion to confirm
print("\nIDs after deletion:")
for doc_id in existing_ids_after_delete:
    print(doc_id)
