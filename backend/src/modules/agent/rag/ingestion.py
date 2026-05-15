import glob
import os
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", "knowledge")
EMBED_MODEL = "all-MiniLM-L6-v2"

COLLECTIONS = {
    "tech": "tech",
    "billing": "billing",
    "hr_support": "hr",
    "general": "general",
}


def ingest():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    for collection_name, folder in COLLECTIONS.items():
        collection = client.get_or_create_collection(
            name=collection_name, embedding_function=ef)
        folder_path = os.path.join(KNOWLEDGE_PATH, folder)

        if not os.path.exists(folder_path):
            print(f"[skip] Folder not found: {folder_path}")
            continue

        md_files = glob.glob(os.path.join(folder_path, "*.md"))
        if not md_files:
            print(f"[skip] No .md files found in: {folder_path}")
            continue

        for file_path in md_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by ## sections to keep tables and their headers together
            raw_sections = re.split(r'(?=^## )', content, flags=re.MULTILINE)
            chunks = [s.strip() for s in raw_sections if s.strip()]

            # Pega o nome sem extensão para usar como base dos IDs
            doc_name = Path(file_path).stem
            ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]

            collection.upsert(documents=chunks, ids=ids)
            print(
                f"[ok] {len(chunks)} chunks from '{Path(file_path).name}' → collection '{collection_name}'")

    print("\nIngestion complete.")


if __name__ == "__main__":
    ingest()
