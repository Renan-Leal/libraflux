from nest.core import Controller, Get, Post
from .book_service import BookService
from .dtos.search_books_dto import SearchBookDTO
from ..auth.auth_guard import get_current_user
from fastapi import Depends


@Controller("/books")
class BookController:

    def __init__(self, service: BookService):
        self.service = service

    @Get("/")
    def list_books(self, page: int = None, size: int = None, user=Depends(get_current_user)):
        """
        /books/?page=1&size=10
        Lista os livros com paginação opcional.
        Se 'page' e 'size' não forem fornecidos, retorna todos os livros.
        """
        if page is not None and size is not None:
            return self.service.list_books_paginated(page, size)
        return self.service.list_books()

    @Get("/top-rated")
    def get_top_rated_books(self, user=Depends(get_current_user)):
        """
        Retorna uma lista de livros bem avaliados (exemplo: rating >= 4).
        """
        return self.service.get_top_rated_books()

    @Get("/price-range")
    def list_books_by_price_range(self, min_price: float = None, max_price: float = None, user=Depends(get_current_user)):
        """
        Lista livros dentro de um intervalo de preços.
        Exemplo: /books/price-range?min_price=10.0&max_price=50.0
        """
        if min_price is not None and max_price is not None:
            return self.service.list_books_by_price_range(min_price, max_price)
        return {"error": "Parâmetros 'min_price' e 'max_price' são necessários."}

    @Get("/search")
    def search_books(self, title: str = None, category: str = None, user=Depends(get_current_user)):
        """
        Busca livros por título e/ou categoria.
        Exemplo: /books/search?title=Python&category=Programming
        """
        return self.service.search_books(title, category)
    
    @Get("/{id}")
    def get_book(self, id: int, user=Depends(get_current_user)):
        """
        Retorna um livro pelo ID.
        Exemplo: /books/1
        """
        return self.service.get_book_by_id(id)
    