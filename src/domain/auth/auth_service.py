import os
import hashlib
from nest.core import Injectable
from .dtos.auth_signup import AuthSignup
from .dtos.auth_login import AuthLogin
from ..user.user import User
from ...infra.repositories.user.user_repository import UserRepository
import jwt
import datetime


@Injectable
class AuthService:
    def __init__(self, userRepository: UserRepository):
        self.userRepository = userRepository
        self.secret = os.environ.get("JWT_SECRET_KEY", "")
        self.algorithm = os.environ.get("JWT_ALGORITHM", "")

    def signup(self, authSignup: AuthSignup):
        """
        Cria um novo usuário com base nos dados fornecidos.
        
        :param authSignup: Dados do usuário a ser criado.
        :return: Um dicionário com os detalhes do usuário criado ou uma mensagem de erro.
        """
        password_hash = hashlib.sha256(
            (authSignup.password + self.secret).encode()
        ).hexdigest()
        user = User(
            authSignup.email,
            authSignup.name,
            password_hash,
            authSignup.role if hasattr(authSignup, "role") else None,
        )
        user_model = user.to_user_model()
        try:
            created_user = self.userRepository.save(user_model)
            if created_user:
                return {
                    "email": created_user.email,
                    "name": created_user.name,
                    "role": (
                        created_user.role.value
                        if hasattr(created_user.role, "value")
                        else str(created_user.role)
                    ),
                    "message": "User created successfully",
                }, 201
            else:
                return {"message": "Failed to create user"}, 400
        except Exception as e:
            return {"message": f"Failed to create user: {str(e)}"}, 400

    def login(self, authLogin: AuthLogin):
        """
        Realiza o login do usuário com base no email e senha fornecidos.
        
        :param authLogin: Dados de login do usuário.
        :return: Um dicionário com o token de acesso ou uma mensagem de erro.
        """
        user = self.userRepository.find_by_email(authLogin.email)

        if not user:
            return {"message": "User not found"}, 404

        password_hash = hashlib.sha256(
            (authLogin.password + self.secret).encode()
        ).hexdigest()

        if user.password != password_hash:
            return {"message": "Invalid credentials"}, 401

        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": expiration_time,
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)

        return {"access_token": token, "token_type": "bearer"}, 200
