import os
from src.domain.auth.auth_service import AuthService
from src.domain.auth.dtos.auth_signup import AuthSignup
from src.infra.repositories.user.user_repository import UserRepository
from src.infra.db import SessionLocal
from src.infra.logs.logging_service import LoggingService


class DefaultAdminManager:
    def __init__(self):
        self.auth_service = AuthService(UserRepository())
        self.logger = LoggingService(file_name="default_admin")

    def create_admin_user(self):
        """
        Cria o usuário admin se não existir.
        """
        with SessionLocal() as session:
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
                signup_response, status_code = self.auth_service.signup(signup_data)

                if status_code == 201:
                    self.logger.info("Admin user created successfully.")
                else:
                    self.logger.error(
                        f"Failed to create admin user: {signup_response['message']}"
                    )
            else:
                self.logger.info("Admin user already exists.")
