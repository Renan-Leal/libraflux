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
        return self.repository.get_by_id(id)

    def search_books(self, title: str = None, category: str = None):
        if (title and title.strip()) and (category and category.strip()):
            return self.repository.list_bycategoryandtitle(title, category)
        elif title and title.strip():
            return self.repository.list_bytitle(title)
        elif category and category.strip():
            return self.repository.list_bycategory(category)
        else:
            return []
        pass

    def list_categories(self):
        pass
