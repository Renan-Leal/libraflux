from nest.core import Controller, Get, Post
from .book_service import BookService
from .dtos.search_books_dto import SearchBookDTO


@Controller("/books")
class BookController:

    def __init__(self, service: BookService):
        self.service = service

    # CORE
    # @Get("/")
    # def list_books(self):
    #     return self.service.list_books()

    @Get("/")
    def list_books(self, page: int = None, size: int = None):
        """
        /books/?page=1&size=10
        Lista os livros com paginação opcional.
        Se 'page' e 'size' não forem fornecidos, retorna todos os livros.
        """
        if page is not None and size is not None:
            return self.service.list_books_paginated(page, size)
        return self.service.list_books()

    @Get("/{id}")
    def get_book(self, id: int):
        return self.service.get_book_by_id(id)

    @Get("/search")
    def search_books(self, title: str = None, category: str = None):
        return self.service.search_books(title, category)

    @Get("/categories")
    def list_categories(self):
        return self.service.list_categories()
