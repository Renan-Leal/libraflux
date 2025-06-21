from nest.core import Injectable
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Tuple
from urllib.parse import urljoin
from ...infra.logs.logging_service import LoggingService
import os


@Injectable
class BookScraper:
    def __init__(self, logger: LoggingService):
        self.base_url = os.environ.get("URL_TO_SCRAPE")
        self.session = requests.Session()
        self.books_data = []
        self.logger = logger

    def __get_page(self, url: str) -> BeautifulSoup:
        """Faz requisição e retorna BeautifulSoup object"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self.logger.error(f"Erro ao acessar {url}: {e}")
            return None

    def __get_categories(self) -> Dict[str, str]:
        """Extrai todas as categorias de livros"""
        soup = self.__get_page(self.base_url)
        if not soup:
            return {}

        categories = {}
        sidebar = soup.find("div", class_="side_categories")
        self.logger.debug(f"A side bar é {sidebar}")
        if sidebar:
            links = sidebar.find_all("a", href=True)
            self.logger.debug(f"Tem {len(links)}, exemplo : {links[5]}")
            for link in links:
                if "catalogue/category" in link.get("href"):
                    category_name = link.text.strip()
                    category_url = urljoin(self.base_url, link.get("href"))
                    categories[category_name] = category_url

        self.logger.info(f"Encontradas {len(categories)} categorias")
        return categories

    def __extract_book_info(self, book_element) -> Dict:
        """Extrai informações de um livro"""
        book_data = {}

        # Título
        title_element = book_element.find("h3").find("a")
        book_data["title"] = title_element.get("title", "") if title_element else ""

        # Preço
        price_element = book_element.find("p", class_="price_color")
        book_data["price"] = price_element.text.strip() if price_element else ""

        # Disponibilidade
        stock_element = book_element.find("p", class_="instock availability")
        book_data["availability"] = stock_element.text.strip() if stock_element else ""

        # Rating (estrelas)
        rating_element = book_element.find("p", class_="star-rating")
        if rating_element:
            rating_classes = rating_element.get("class", [])
            rating_words = ["Zero", "One", "Two", "Three", "Four", "Five"]
            for word in rating_words:
                if word in rating_classes:
                    book_data["rating"] = rating_words.index(word)
                    break
        else:
            book_data["rating"] = 0

        # Link do livro
        if title_element:
            book_data["link"] = urljoin(self.base_url, title_element.get("href", ""))

        return book_data

    def __get_books_from_page(self, page_url: str) -> List[Dict]:
        """Extrai todos os livros de uma página"""
        soup = self.__get_page(page_url)
        if not soup:
            return []

        books = []
        book_elements = soup.find_all("article", class_="product_pod")

        for book_element in book_elements:
            book_info = self.__extract_book_info(book_element)
            if book_info["title"]:  # Só adiciona se tiver título
                books.append(book_info)

        return books

    def __get_all_pages_from_category(self, category_url: str) -> List[Dict]:
        """Percorre todas as páginas de uma categoria"""
        all_books = []
        current_url = category_url
        page_num = 1

        while current_url:
            self.logger.info(f"Processando página {page_num} - {current_url}")

            books = self.__get_books_from_page(current_url)
            all_books.extend(books)

            # Verifica se há próxima página
            soup = self.__get_page(current_url)
            if soup:
                next_link = soup.find("li", class_="next")
                self.logger.debug(f"pagina {page_num} : {next_link}")
                if next_link and next_link.find("a"):
                    next_url = next_link.find("a").get("href")
                    current_url = urljoin(current_url, next_url)
                    page_num += 1
                else:
                    current_url = None
            else:
                break

            time.sleep(0.5)

        return all_books

    def __scrape_category(self, category_name: str, category_url: str) -> List[Dict]:
        """Faz scraping de uma categoria específica"""
        self.logger.info(f"Iniciando scraping da categoria: {category_name}")

        books = self.__get_all_pages_from_category(category_url)

        for book in books:
            book["category"] = category_name

        self.logger.info(f"Categoria {category_name}: {len(books)} livros encontrados")
        return books

    def execute(self):
        """Função principal para executar o scraping"""

        categories = self.__get_categories()

        print("Categorias disponíveis:")
        for i, (name, url) in enumerate(categories.items(), 1):
            print(f"{i}. {name}")

        if categories:
            first_category = list(categories.items())[0]
            self.logger.debug(first_category)
            return self.__scrape_category(first_category[0], first_category[1])
