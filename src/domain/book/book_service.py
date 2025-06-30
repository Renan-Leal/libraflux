from nest.core import Injectable
from ...infra.repositories.book_repository import BookRepository


@Injectable
class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def list_books(self):
        """List all books in the database."""
        #TODO
        # descobrir como realizar a paginação
        return self.repository.list_all()

    def get_book_by_id(self, id: int):
        pass

    def search_books(self, title: str = None, category: str = None):
        pass

    def list_categories(self):
        pass
