from nest.core import Injectable
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
