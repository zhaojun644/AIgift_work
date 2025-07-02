from __future__ import annotations

import argparse
from typing import List

import openai
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sqlmodel import Session, select, create_engine

from app.models import Product

DATABASE_URL = "sqlite:///gift.db"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "products"
EMBED_DIM = 3072


def get_products() -> List[Product]:
    """Return all products from the database."""
    engine = create_engine(DATABASE_URL, echo=False)
    with Session(engine) as session:
        return list(session.exec(select(Product)))


def embed_text(text: str) -> List[float]:
    """Return embedding vector for a given text using OpenAI."""
    response = openai.Embedding.create(model="text-embedding-3-large", input=text)
    return response["data"][0]["embedding"]


def upsert_products(products: List[Product]) -> None:
    """Embed product descriptions and upsert them into Qdrant."""
    client = QdrantClient(url=QDRANT_URL)

    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=rest.VectorParams(size=EMBED_DIM, distance=rest.Distance.COSINE),
        )

    points = []
    for product in products:
        embedding = embed_text(product.description)
        payload = {
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "tags": product.tags,
        }
        points.append(rest.PointStruct(id=product.id, vector=embedding, payload=payload))

    client.upsert(collection_name=COLLECTION_NAME, points=points)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed products and upsert to Qdrant")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    args = parser.parse_args()

    openai.api_key = args.api_key

    products = get_products()
    if not products:
        print("No products found.")
        return

    upsert_products(products)


if __name__ == "__main__":
    main()
