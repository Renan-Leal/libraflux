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
from .infra.db import Base, engine, SessionLocal
from .infra.repositories.user.user_repository import UserRepository
from .domain.auth.auth_module import AuthModule
from src.domain.auth.auth_service import AuthService
from src.domain.auth.dtos.auth_signup import AuthSignup
from .infra.logs.logging_service import LoggingService

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
logger = LoggingService("libraflux")

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


# Cria o usuário admin se não existir
def create_admin_user():
    """
    Cria o usuário admin se não existir.
    Esta função verifica se o usuário admin já existe e, se não existir, cria um novo usuário admin.
    """
    with SessionLocal() as session:
        auth_service = AuthService(UserRepository())

        # Verifica se o usuário admin já existe
        admin_user = UserRepository().find_by_email("admin@admin.com")
        if not admin_user:
            # Cria o usuário admin chamando o método signup
            signup_data = AuthSignup(
                email=os.environ.get("ADMIN_EMAIL"),
                name=os.environ.get("ADMIN_NAME"),
                password=os.environ.get("ADMIN_PASSWORD"),
                role=os.environ.get("ADMIN_ROLE"),
            )
            signup_response, status_code = auth_service.signup(signup_data)

            if status_code == 201:
                print("Admin user created successfully.")
                # logger.info("Admin user created successfully.")
            else:
                print(f"Failed to create admin user: {signup_response['message']}")
                # logger.error(f"Failed to create admin user: {signup_response['message']}")
        else:
            print("Admin user already exists.")
            # logger.warning("Admin user already exists.")


# Configura o prefixo global se estiver definido
if api_prefix:
    api_prefix = api_prefix.strip("/")
    global_router = APIRouter(prefix=f"/{api_prefix}" if api_prefix else "")
    global_router.include_router(app.get_server().router)
    app.get_server().router.routes = []
    app.get_server().include_router(global_router)

# Chama a função para criar o admin user
create_admin_user()

http_server = app.get_server()
