from nest.core import Injectable
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Tuple
from urllib.parse import urljoin
from ...infra.logs.logging_service import LoggingService
import os
import re


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

    def __extract_book_details(self, book_url) -> Dict:
        """Extrai informações detalhadas do livro"""
        book_data = {}

        book_url_aux = f"{self.base_url}/catalogue/{book_url.split('../')[-1]}"
        soup_page_book = self.__get_page(book_url_aux)

        # Título do livro
        book_data["title"] = (
            soup_page_book.find("h1").get_text(strip=True)
            if soup_page_book.find("h1")
            else ""
        )

        # Categoria
        category_element = soup_page_book.find("ul", class_="breadcrumb")
        if category_element:
            category_links = category_element.find_all("a")
            if len(category_links) >= 3:
                book_data["category"] = category_links[2].get_text(strip=True)
            else:
                book_data["category"] = ""

        # Preço
        book_data["price"] = (
            soup_page_book.find("p", class_="price_color")
            .get_text(strip=True)
            .replace("Â", "")
            if soup_page_book.find("p", class_="price_color")
            else ""
        )

        # Stock
        availability_element = soup_page_book.find("p", class_="instock availability")
        if availability_element:
            availability_text = availability_element.get_text(
                strip=True
            )  # Ex.: "In stock (22 available)"
            book_data["availability"] = (
                "In stock" if "In stock" in availability_text else "Out of stock"
            )
            # Extrair a quantidade (número entre parênteses)
            quantity_match = re.search(r"\((\d+) available\)", availability_text)
            book_data["quantity"] = (
                int(quantity_match.group(1)) if quantity_match else 0
            )
        else:
            book_data["availability"] = ""
            book_data["quantity"] = 0

        # Rating
        rating_element = soup_page_book.find("p", class_="star-rating")
        rating_words = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        book_data["rating"] = (
            next(
                (
                    rating_words[word]
                    for word in rating_words
                    if word in rating_element.get("class", [])
                ),
                0,
            )
            if rating_element
            else 0
        )
        # Description - extrai e corrige encoding
        desc_element = soup_page_book.find("div", id="product_description")
        if desc_element and desc_element.find_next("p"):
            raw_desc = (
                desc_element.find_next("p").get_text(strip=True).replace(";", ".")
            )
            corrected_desc = raw_desc.encode("latin1", errors="ignore").decode(
                "utf-8", errors="ignore"
            )
            book_data["description"] = corrected_desc
        else:
            book_data["description"] = ""

        # Product Information
        table = soup_page_book.find("table", class_="table table-striped")
        if table:
            for row in table.find_all("tr"):
                key = row.find("th").get_text(strip=True)
                value = row.find("td").get_text(strip=True)
                book_data[key] = value

        # Image
        img_element = soup_page_book.find("img")
        img_src = (
            img_element["src"].replace("../", "")
            if img_element and "src" in img_element.attrs
            else ""
        )
        book_data["image"] = f"{self.base_url}{img_src}"

        return book_data

    def __extract_book_info(self, book_element) -> Dict:
        """Chama o método para extrair a informação do livro, passando a url dele"""
        book_url = book_element.find("h3").find("a").get("href")
        book_details = self.__extract_book_details(book_url)

        # Resultado filtrado com limpeza de "Â"
        books_filtered = {
            "id": book_details.get("UPC"),
            "title": book_details.get("title"),
            "category": book_details.get("category", ""),
            "rating": book_details.get("rating", 0),
            "price_excl_tax": book_details.get("Price (excl. tax)", "").replace(
                "Â£", ""
            ),
            "price_incl_tax": book_details.get("Price (incl. tax)", "").replace(
                "Â£", ""
            ),
            "tax": book_details.get("Tax", "").replace("Â£", ""),
            "availability": book_details.get("quantity", 0),
            "reviews_qtd": book_details.get("Number of reviews"),
            "description": book_details.get("description"),
            "image": book_details.get("image"),
        }

        return books_filtered

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

        count = 0
        while current_url and count < 1:
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

            count += 1
            time.sleep(0.5)

        return all_books

    def __scrape_category(self, category_name: str, category_url: str) -> List[Dict]:
        """Faz scraping de uma categoria específica"""
        self.logger.info(f"Iniciando scraping da categoria: {category_name}")

        books = self.__get_all_pages_from_category(category_url)

        self.logger.info(f"Quantidade de livros encontrados - {len(books)}")
        return books

    def execute(self):
        """Função principal para executar o scraping"""

        categories = self.__get_categories()

        if categories:
            first_category = list(categories.items())[0]
            self.logger.debug(first_category)
            return self.__scrape_category(first_category[0], first_category[1])
