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
        return self.service.signup(authSignup)

    @Post("/login")
    def login(self, authLogin: AuthLogin):
        return self.service.login(authLogin)
