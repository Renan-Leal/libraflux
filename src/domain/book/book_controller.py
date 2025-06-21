from nest.core import Controller, Get, Post
from .book_service import BookService
from .dtos.search_books_dto import SearchBookDTO


@Controller("/books")
class BookController:

    def __init__(self, service: BookService):
        self.service = service

    # CORE
    @Get("/")
    def list_books(self):
        print("test")
        return self.service.list_books()

    @Get("/<id>")
    def get_book(self, id: int):
        return self.service.get_book_by_id(id)

    @Get("/search")
    def search_books(self, search_book_dto: SearchBookDTO):
        return self.service.search_books(
            search_book_dto.title, search_book_dto.category
        )

    @Get("/categories")
    def list_categories(self):
        return self.service.list_categories()
