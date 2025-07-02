from __future__ import annotations

from typing import Optional, List

from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    stock: int
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
