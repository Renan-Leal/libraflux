import os
from dotenv import load_dotenv
from fastapi import APIRouter
from nest.core import PyNestFactory, Module
from .domain.book.book_module import BookModule
from .domain.scraping.scraping_module import ScrapingModule
from .infra.logs.logging_module import LoggingModule

load_dotenv()


@Module(imports=[LoggingModule, BookModule, ScrapingModule])
class AppModule:
    pass


api_version = os.environ.get("API_VERSION", "1.0.0")
debug = os.environ.get("DEBUG", "False").lower() == "true"
api_title = os.environ.get("API_TITLE", "Dataflux API")
api_description = os.environ.get("API_DESCRIPTION", "Dataflux Scraping data flow")
api_prefix = os.environ.get("API_VERSION_PREFIX", "")

# Cria a aplicação PyNest
app = PyNestFactory.create(
    AppModule,
    description=api_description,
    title=api_title,
    version=api_version,
    debug=debug,
)

# Configura o prefixo global se estiver definido
if api_prefix:
    api_prefix = api_prefix.strip("/")
    global_router = APIRouter(prefix=f"/{api_prefix}" if api_prefix else "")
    global_router.include_router(app.get_server().router)
    app.get_server().router.routes = []
    app.get_server().include_router(global_router)

http_server = app.get_server()
