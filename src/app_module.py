import os
from dotenv import load_dotenv
from fastapi import APIRouter
from nest.core import PyNestFactory, Module
from .domain.book.book_module import BookModule
from .domain.scraping.scraping_module import ScrapingModule
from .domain.categories.categories_module import CategoriesModule
from .domain.health.health_module import HealthModule
from .domain.stats.stats_module import StatsModule
from .infra.logs.logging_module import LoggingModule
from .infra.models import *
from .infra.db import Base, engine
from .domain.auth.auth_module import AuthModule


load_dotenv()


@Module(
    imports=[
        LoggingModule,
        BookModule,
        ScrapingModule,
        HealthModule,
        CategoriesModule,
        StatsModule,
        AuthModule,
    ]
)
class AppModule:
    pass


api_version = os.environ.get("API_VERSION", "1.0.0")
debug = os.environ.get("DEBUG", "False").lower() == "true"
api_title = os.environ.get("API_TITLE", "Libraflux API")
api_description = os.environ.get("API_DESCRIPTION", "Libraflux Scraping data flow")
api_prefix = os.environ.get("API_VERSION_PREFIX", "")


# Cria a aplicação PyNest
app = PyNestFactory.create(
    AppModule,
    description=api_description,
    title=api_title,
    version=api_version,
    debug=debug,
)

# Cria as tabelas se ainda não existirem
Base.metadata.create_all(bind=engine)

# Configura o prefixo global se estiver definido
if api_prefix:
    api_prefix = api_prefix.strip("/")
    global_router = APIRouter(prefix=f"/{api_prefix}" if api_prefix else "")
    global_router.include_router(app.get_server().router)
    app.get_server().router.routes = []
    app.get_server().include_router(global_router)

http_server = app.get_server()
