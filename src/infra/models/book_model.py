from sqlalchemy import Column, String, Integer, Float, Text
from ..db import Base


class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(36), nullable=False)
    price_excl_tax = Column(Float, nullable=False)
    price_incl_tax = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    availability = Column(Integer, nullable=False)
    reviews_qtd = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    image = Column(Text, nullable=True)

    # ONLY DEBUG
    # def __repr__(self):
    #     return f"{self.title} | ID: {self.id}"
