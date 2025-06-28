from ..db import db
from nest.core import Injectable


class BookModel(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    price_excl_tax = db.Column(db.Float, nullable=False)
    price_incl_tax = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    reviews_qtd = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=True)
