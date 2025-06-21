from nest.core import Injectable


@Injectable
class BookService:
    def __init__(self):
        pass

    def list_books(self):
        pass

    def get_book_by_id(self, id: int):
        pass

    def search_books(self, title: str = None, category: str = None):
        pass

    def list_categories(self):
        pass
