from nest.core import Injectable
from sqlalchemy import and_
from ..models.book_model import BookModel
from ..db import SessionLocal


@Injectable
class BookRepository:
    def __init__(self):
        pass

    def create_many(self, books_data: list[BookModel]):
        with SessionLocal() as session:
            for book in books_data:
                # Verifica se o UUID já existe no banco
                exists = session.query(BookModel).filter_by(uuid=book.uuid).first()
                if not exists:
                    session.add(book)  # Insere apenas se não existir
            session.commit()

    def list_all(self) -> list[BookModel]:
        with SessionLocal() as session:
            return session.query(BookModel).all()

    def list_bycategory(self, category: str) -> list[BookModel]:
        with SessionLocal() as session:
            return session.query(BookModel).filter(BookModel.category == category).all()

    def list_bytitle(self, title: str) -> list[BookModel]:
        with SessionLocal() as session:
            return session.query(BookModel).filter(BookModel.title == title).all()

    def list_bycategoryandtitle(self, title: str, category: str) -> list[BookModel]:
        with SessionLocal() as session:
            return (
                session.query(BookModel)
                .filter(and_(BookModel.category == category, BookModel.title == title))
                .all()
            )
