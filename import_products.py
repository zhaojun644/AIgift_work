from __future__ import annotations

import argparse
import csv
from typing import List

from sqlmodel import SQLModel, Session, create_engine

from app.models import Product

DATABASE_URL = "sqlite:///gift.db"

def import_products(csv_path: str) -> None:
    """Import products from a CSV file into the database."""
    engine = create_engine(DATABASE_URL, echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        with open(csv_path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tags = [t.strip() for t in row.get("tags", "").split(',') if t.strip()]
                product = Product(
                    name=row.get("name", ""),
                    description=row.get("description", ""),
                    price=float(row.get("price", 0)),
                    stock=int(row.get("stock", 0)),
                    tags=tags,
                )
                session.add(product)
        session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import products from CSV")
    parser.add_argument("csv_path", help="Path to CSV file containing products")
    args = parser.parse_args()
    import_products(args.csv_path)


if __name__ == "__main__":
    main()
