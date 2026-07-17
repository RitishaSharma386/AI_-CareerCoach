import os
import chromadb
# Point to your existing collection path
CHROMA_PATH = os.path.join(".", "data", "processed")

def test_persistence():
    # 1. Initialize client pointing to the existing folder
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # 2. Try to get the existing collection
    try:
        collection = client.get_collection(name="job_listings")
        count = collection.count()
        print(f"Success! Found collection with {count} items stored on disk.")
    except Exception as e:
        print(f"Failed to find collection: {e}")

if __name__ == "__main__":
    test_persistence()