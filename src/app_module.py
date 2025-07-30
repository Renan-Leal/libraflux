import os
from dotenv import load_dotenv
from fastapi import APIRouter
from nest.core import PyNestFactory, Module
from .domain.book.book_module import BookModule
from .domain.scraping.scraping_module import ScrapingModule
from .domain.categories.categories_module import CategoriesModule
from .domain.health.health_module import HealthModule
from .domain.stats.stats_module import StatsModule
from .domain.ml.ml_module import MlModule
from .infra.logs.logging_module import LoggingModule
from .infra.models import *
from .infra.db import Base, engine
from .domain.auth.auth_module import AuthModule
from .infra.logs.logging_service import LoggingService
from .utils.create_default_admin import DefaultAdminManager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

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
        MlModule,
    ]
)
class AppModule:
    pass


api_version = os.environ.get("API_VERSION", "1.0.0")
debug = os.environ.get("DEBUG", "False").lower() == "true"
api_title = os.environ.get("API_TITLE", "Libraflux API")
api_description = os.environ.get("API_DESCRIPTION", "Libraflux Scraping data flow")
api_prefix = os.environ.get("API_VERSION_PREFIX", "")
logger = LoggingService("libraflux")

# cria PyNest normalmente
app = PyNestFactory.create(
    AppModule,
    description=api_description,
    title=api_title,
    version=api_version,
    debug=debug,
    docs_url=None,  # desativa docs internas
    redoc_url=None,
    openapi_url=None,
)

Base.metadata.create_all(bind=engine)

# Cria um novo app wrapper para aplicar o prefixo e expor docs
if api_prefix:
    api_prefix = api_prefix.strip("/")
    wrapper_app = FastAPI(
        title=api_title,
        description=api_description,
        version=api_version,
        debug=debug,
        docs_url=f"/docs",
        redoc_url=None,
        openapi_url=f"/openapi.json",
    )

    # monta o app PyNest no wrapper
    wrapper_app.mount(f"/{api_prefix}", app.get_server())

    # injeta manualmente o schema da app montada no wrapper
    openapi_schema = get_openapi(
        title=api_title,
        version=api_version,
        description=api_description,
        routes=app.get_server().routes,
    )
    openapi_schema["servers"] = [{"url": f"/{api_prefix}", "description": "API Server"}]
    wrapper_app.openapi_schema = openapi_schema
else:
    wrapper_app = app.get_server()



# admin manager etc (deixa como está)
admin_manager = DefaultAdminManager()
admin_manager.create_admin_user()

http_server = wrapper_app
