from nest.core import Controller, Get, Post
from .dtos.auth_signup import AuthSignup
from .auth_service import AuthService

@Controller("/auth")
class AuthController:

    def __init__(self, service: AuthService):
        self.service = service
    
    @Post('/signup')
    def check(self, authSignup: AuthSignup):
        return self.service.signup(authSignup)
