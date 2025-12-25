import os
import chromadb
from chromadb.utils import embedding_functions

# Init Vetor Database (Persistent -> Saves to disk)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# all-MiniLM-L6-v2
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or get the collection
collection = chroma_client.get_or_create_collection(name="codebase", embedding_function=sentence_transformer_ef)

def index_codebase(root_dir="."):
    print(" Scanning codebase...")

    files_processed = 0
    ids = []
    documents = []
    metadatas = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and "test" not in file and "agent" not in file and "indexer" not in file:
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                ids.append(file_path)
                documents.append(content)
                metadatas.append({"filename": file_path})
                files_processed += 1
                print(f" Indexed: {file_path}")

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f" Successfully indexed {files_processed} files into ChromaDB. ")
    else:
        print(" No vaild Python files found to index. ")
    
if __name__ == "__main__":
    index_codebase()