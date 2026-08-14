import json
import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATABASE_PATH = Path(__file__).parent.parent / "database" / "schemes.json"

VECTOR_DIR = Path(__file__).parent.parent.parent / "vector_db"
VECTOR_DIR.mkdir(exist_ok=True)

INDEX_PATH = VECTOR_DIR / "schemes.index"
METADATA_PATH = VECTOR_DIR / "metadata.pkl"

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_schemes():
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_vector_db():
    schemes = load_schemes()

    texts = []
    metadata = []

    for scheme in schemes:
        text = f"""
Scheme Name: {scheme['name']}
Benefit: {scheme['benefit']}
Occupation: {scheme['occupation']}
Education: {scheme['education']}
Maximum Income: {scheme['max_income']}
States: {", ".join(scheme['states'])}
"""
        texts.append(text)
        metadata.append(scheme)

    embeddings = model.encode(texts)

    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("✅ Vector database created successfully!")


def search_schemes(query: str, top_k: int = 3):
    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    query_embedding = model.encode([query])

    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = []

    for idx in indices[0]:
        if idx != -1:
            results.append(metadata[idx])

    return results