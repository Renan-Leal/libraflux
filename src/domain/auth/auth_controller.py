from nest.core import Controller, Get, Post
from fastapi import Request
from .dtos.auth_signup import AuthSignup
from .dtos.auth_login import AuthLogin
from .auth_service import AuthService


@Controller("/auth")
class AuthController:

    def __init__(self, service: AuthService):
        self.service = service

    @Post("/signup")
    def check(self, authSignup: AuthSignup, request: Request):
        """
        Endpoint para registrar um novo usuário.
        Este endpoint permite que novos usuários se registrem no sistema.
        """
        # Extrair contexto da requisição para logs enriquecidos
        request_context = self._extract_request_context(request)
        
        # Configurar contexto no service se disponível
        if hasattr(request.state, 'correlation_id'):
            self.service.set_request_context(
                request.state.correlation_id,
                getattr(request.state, 'user_context', {})
            )
        
        return self.service.signup(authSignup, request_context)

    @Post("/login")
    def login(self, authLogin: AuthLogin, request: Request):
        """
        Endpoint para autenticar um usuário.
        Este endpoint permite que usuários façam login no sistema.
        """
        # Extrair contexto da requisição para logs de segurança
        request_context = self._extract_request_context(request)
        
        # Configurar contexto no service se disponível
        if hasattr(request.state, 'correlation_id'):
            self.service.set_request_context(
                request.state.correlation_id,
                getattr(request.state, 'user_context', {})
            )
        
        return self.service.login(authLogin, request_context)

    def _extract_request_context(self, request: Request) -> dict:
        """Extrai contexto útil da requisição para logs"""
        context = {}
        
        # IP do cliente
        if hasattr(request, 'client') and request.client:
            context['client_ip'] = request.client.host
        
        # Headers relevantes
        headers = dict(request.headers)
        context['user_agent'] = headers.get('user-agent', 'unknown')
        context['content_type'] = headers.get('content-type', 'unknown')
        
        # Informações adicionais se disponíveis no state
        if hasattr(request.state, 'user_context'):
            user_context = request.state.user_context
            context['authenticated'] = user_context.get('authenticated', False)
            context['current_user_role'] = user_context.get('role')
            context['current_user_id'] = user_context.get('user_id')
        
        return context
