from nest.core import Injectable
from ..models.book_model import BookModel
from ..db import SessionLocal


@Injectable
class BookRepository:
    def __init__(self):
        pass

    def create_many(self, books_data: list[BookModel]):
        with SessionLocal() as session:
            session.add_all(books_data)
            session.commit()
