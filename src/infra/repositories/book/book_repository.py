from nest.core import Injectable
from sqlalchemy import and_
from ...models.book_model import BookModel
from ...db import SessionLocal


@Injectable
class BookRepository:
    def __init__(self):
        pass

    def create_many(self, books_data: list[BookModel]):
        """
        Insere vários livros no banco de dados, evitando duplicatas.
        """
        with SessionLocal() as session:
            for book in books_data:
                # Verifica se o UUID já existe no banco
                exists = session.query(BookModel).filter_by(uuid=book.uuid).first()
                if not exists:
                    session.add(book)  # Insere apenas se não existir
            session.commit()

    def list_all(self) -> list[BookModel]:
        """
        Lista todos os livros no banco de dados.
        """
        with SessionLocal() as session:
            return session.query(BookModel).all()

    def get_by_id(self, book_int: int) -> BookModel:
        """
        Retorna um livro pelo ID.
        Exemplo: /books/1
        """
        with SessionLocal() as session:
            return session.query(BookModel).filter_by(id=book_int).first()

    def list_bycategory(self, category: str) -> list[BookModel]:
        """
        Lista livros por categoria.
        Exemplo: /books/search?category={Category}
        """
        with SessionLocal() as session:
            return session.query(BookModel).filter(BookModel.category == category).all()

    def list_bytitle(self, title: str) -> list[BookModel]:
        """
        Lista livros por título.
        Exemplo: /books/search?title={Title}
        """
        with SessionLocal() as session:
            return session.query(BookModel).filter(BookModel.title == title).all()

    def list_bycategoryandtitle(self, title: str, category: str) -> list[BookModel]:
        """
        Lista livros por título e categoria.
        Exemplo: /books/search?title={Title}&category={Category}
        """
        with SessionLocal() as session:
            return (
                session.query(BookModel)
                .filter(and_(BookModel.category == category, BookModel.title == title))
                .all()
            )

    def get_top_rated_books(self) -> list[BookModel]:
        """
        Retorna uma lista de livros bem avaliados (exemplo: rating >= 4).
        """
        with SessionLocal() as session:
            return (
                session.query(BookModel)
                .filter(BookModel.id >= 4)
                .order_by(BookModel.rating.desc())
                .all()
            )
    
    def list_by_price_range(self, min_price: float, max_price: float) -> list[BookModel]:
        """
        Lista livros dentro de um intervalo de preços.
        Exemplo: /books/price-range?min_price=10.0&max_price=50.0
        """
        with SessionLocal() as session:
            return (
                session.query(BookModel)
                .filter(BookModel.price_incl_tax >= min_price, BookModel.price_incl_tax <= max_price)
                .order_by(BookModel.price_incl_tax)                
                .all()
            )
        