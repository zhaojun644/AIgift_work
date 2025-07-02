from __future__ import annotations

from typing import List

import openai
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

DATABASE_URL = "sqlite:///gift.db"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "products"
EMBED_DIM = 3072


def embed_text(text: str) -> List[float]:
    """Return embedding vector for a given text using OpenAI."""
    response = openai.Embedding.create(model="text-embedding-3-large", input=text)
    return response["data"][0]["embedding"]


def vector_search(text: str, budget: float, limit: int = 5) -> List[dict]:
    """Return top matching product payloads within the budget."""
    client = QdrantClient(url=QDRANT_URL)
    query_vector = embed_text(text)
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        with_payload=True,
        query_filter=rest.Filter(
            must=[rest.FieldCondition(key="price", range=rest.Range(lte=budget))]
        ),
    )
    return [point.payload for point in search_result]
