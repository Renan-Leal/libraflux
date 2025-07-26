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
from .infra.middleware.logging_middleware import LoggingMiddleware

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

# Criar logger principal da aplicação
logger = LoggingService("libraflux")

# Cria a aplicação PyNest
app = PyNestFactory.create(
    AppModule,
    description=api_description,
    title=api_title,
    version=api_version,
    debug=debug,
)

# Adicionar middleware de logging
app.get_server().add_middleware(LoggingMiddleware, logger=logger)

# Log do início da aplicação
logger.info(
    f"Starting {api_title} v{api_version}",
    operation="application_startup",
    app_config={
        "version": api_version,
        "debug": debug,
        "api_prefix": api_prefix,
        "environment": os.environ.get("ENVIRONMENT", "development")
    }
)

# Cria as tabelas se ainda não existirem
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully", operation="database_init")
except Exception as e:
    logger.error(
        f"Failed to create database tables: {str(e)}",
        operation="database_init_error",
        error_data={
            "error_message": str(e),
            "error_type": type(e).__name__
        }
    )

# Cria o usuário admin se não existir
def create_admin_user():
    """
    Cria o usuário admin se não existir.
    Esta função verifica se o usuário admin já existe e, se não existir, cria um novo usuário admin.
    """
    try:
        with SessionLocal() as session:
            auth_service = AuthService(UserRepository(), logger)

            # Verifica se o usuário admin já existe
            admin_email = os.environ.get("ADMIN_EMAIL")
            if not admin_email:
                logger.warning(
                    "Admin email not configured in environment variables",
                    operation="admin_user_setup",
                    reason="missing_admin_email_config"
                )
                return

            admin_user = UserRepository().find_by_email(admin_email)
            if not admin_user:
                # Cria o usuário admin chamando o método signup
                signup_data = AuthSignup(
                    email=admin_email,
                    name=os.environ.get("ADMIN_NAME", "Administrator"),
                    password=os.environ.get("ADMIN_PASSWORD"),
                    role=os.environ.get("ADMIN_ROLE", "admin")
                )
                
                signup_response, status_code = auth_service.signup(signup_data)

                if status_code == 201:
                    logger.info(
                        "Admin user created successfully",
                        operation="admin_user_created",
                        admin_data={
                            "email": logger._mask_email(admin_email),
                            "name": signup_data.name,
                            "role": signup_data.role
                        }
                    )
                else:
                    logger.error(
                        f"Failed to create admin user: {signup_response.get('message', 'Unknown error')}",
                        operation="admin_user_creation_failed",
                        error_data={
                            "status_code": status_code,
                            "response": signup_response
                        }
                    )
            else:
                logger.info(
                    "Admin user already exists, skipping creation",
                    operation="admin_user_exists",
                    admin_data={
                        "email": logger._mask_email(admin_email)
                    }
                )
    except Exception as e:
        logger.error(
            f"Error during admin user setup: {str(e)}",
            operation="admin_user_setup_error",
            error_data={
                "error_message": str(e),
                "error_type": type(e).__name__
            }
        )

# Configura o prefixo global se estiver definido
if api_prefix:
    api_prefix = api_prefix.strip("/")
    global_router = APIRouter(prefix=f"/{api_prefix}" if api_prefix else "")
    global_router.include_router(app.get_server().router)
    app.get_server().router.routes = []
    app.get_server().include_router(global_router)
    
    logger.info(
        f"API prefix configured: /{api_prefix}",
        operation="api_prefix_setup",
        config_data={
            "prefix": api_prefix
        }
    )

# Chama a função para criar o admin user
create_admin_user()

logger.info(
    "Application startup completed successfully",
    operation="application_ready"
)

http_server = app.get_server()
