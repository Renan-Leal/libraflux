from nest.core import Controller, Get, Post
from .dtos.auth_signup import AuthSignup
from .dtos.auth_login import AuthLogin
from .auth_service import AuthService


@Controller("/auth")
class AuthController:

    def __init__(self, service: AuthService):
        self.service = service

    @Post("/signup")
    def check(self, authSignup: AuthSignup):
        """
        Endpoint para registrar um novo usuário.
        Este endpoint permite que novos usuários se registrem no sistema.
        """
        return self.service.signup(authSignup)

    @Post("/login")
    def login(self, authLogin: AuthLogin):
        """
        Endpoint para autenticar um usuário.
        Este endpoint permite que usuários façam login no sistema.
        """
        return self.service.login(authLogin)
