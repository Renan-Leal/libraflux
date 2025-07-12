from nest.core import Injectable
from ...infra.repositories.book_repository import BookRepository


@Injectable
class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def list_books(self):
        """List all books in the database."""
        return self.repository.list_all()

    def list_books_paginated(self, page: int, size: int):
        """
        Retorna uma lista paginada de livros.
        """
        start = (page - 1) * size
        end = start + size
        books = self.list_books()  # Método que retorna todos os livros
        return books[start:end]

    def get_book_by_id(self, id: int):
        """
        Retorna um livro pelo ID.
        Exemplo: /books/1
        """
        return self.repository.get_by_id(id)

    def search_books(self, title: str = None, category: str = None):       
        """
        Busca livros por título e/ou categoria.
        Exemplo: /books/search?title={Title}&category={Category}
        """ 
        if (title and title.strip()) and (category and category.strip()):
            return self.repository.list_bycategoryandtitle(title, category)
        elif title and title.strip():
            return self.repository.list_bytitle(title)
        elif category and category.strip():
            return self.repository.list_bycategory(category)
        else:
            return []

    def get_top_rated_books(self):
        """
        Retorna uma lista de livros bem avaliados (exemplo: rating >= 4).
        """
        return self.repository.get_top_rated_books()

    def list_books_by_price_range(self, min_price: float, max_price: float):
        """
        Lista livros dentro de um intervalo de preços.
        Exemplo: /books/price-range?min_price=10.0&max_price=50.0
        """
        return self.repository.list_by_price_range(min_price, max_price)