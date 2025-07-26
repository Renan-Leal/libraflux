import time
import uuid
import os
import jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any, Optional
from ..logs.logging_service import LoggingService
import json


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: LoggingService = None):
        super().__init__(app)
        self.logger = logger or LoggingService("http_middleware")
        self.jwt_secret = os.environ.get("JWT_SECRET_KEY", "")
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar correlation ID único para esta requisição
        correlation_id = LoggingService.generate_correlation_id()
        
        # Configurar correlation ID no logger
        self.logger.set_correlation_id(correlation_id)
        
        # Adicionar correlation ID aos headers da requisição para propagação
        request.state.correlation_id = correlation_id
        
        # Extrair informações do usuário autenticado
        user_context = self._extract_user_context(request)
        
        # Adicionar contexto do usuário ao request state para outros services
        request.state.user_context = user_context
        
        # Capturar dados da requisição
        start_time = time.time()
        request_data = await self._extract_request_data(request)
        
        # Log de entrada da requisição COM informações do usuário
        user_info = self._format_user_info(user_context)
        self.logger.info(
            f"Incoming request: {request.method} {request.url.path} - User: {user_info}",
            operation="http_request_start",
            request_data=request_data,
            user_context=user_context
        )

        # Processar a requisição
        try:
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = (time.time() - start_time) * 1000  # em ms
            
            # Capturar dados da resposta
            response_data = self._extract_response_data(response, process_time)
            
            # Log de saída da requisição COM informações do usuário
            log_level = self._determine_log_level(response.status_code)
            getattr(self.logger, log_level)(
                f"Request completed: {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms) - User: {user_info}",
                operation="http_request_complete",
                request_data=request_data,
                response_data=response_data,
                user_context=user_context
            )
            
            # Adicionar correlation ID ao header da resposta
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Log de erro COM informações do usuário
            process_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)} - User: {user_info}",
                operation="http_request_error",
                request_data=request_data,
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": process_time
                },
                user_context=user_context
            )
            raise

    def _extract_user_context(self, request: Request) -> Dict[str, Any]:
        """Extrai contexto completo do usuário da requisição"""
        user_context = {
            "authenticated": False,
            "user_id": None,
            "email": None,
            "role": None,
            "display_name": "Anonymous"
        }
        
        # Tentar extrair informações do token JWT se disponível
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                # Decodificar o JWT
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=[self.jwt_algorithm],
                    options={"verify_exp": True}
                )
                
                # Extrair informações do usuário
                user_context.update({
                    "authenticated": True,
                    "user_id": payload.get("sub"),
                    "email": payload.get("email"),
                    "role": payload.get("role"),
                    "display_name": self._create_display_name(payload),
                    "token_exp": payload.get("exp"),
                    "jwt_valid": True
                })
                
            except jwt.ExpiredSignatureError:
                user_context.update({
                    "jwt_valid": False,
                    "jwt_error": "token_expired",
                    "display_name": "Expired Token"
                })
            except jwt.InvalidTokenError as e:
                user_context.update({
                    "jwt_valid": False,
                    "jwt_error": "invalid_token",
                    "jwt_error_detail": str(e),
                    "display_name": "Invalid Token"
                })
            except Exception as e:
                user_context.update({
                    "jwt_valid": False,
                    "jwt_error": "decode_error",
                    "jwt_error_detail": str(e),
                    "display_name": "Token Error"
                })
        
        # Adicionar informações de IP para contexto adicional
        user_context["client_ip"] = self._get_client_ip(request)
        
        return user_context

    def _create_display_name(self, payload: Dict[str, Any]) -> str:
        """Cria um nome de exibição amigável para o usuário"""
        email = payload.get("email", "")
        role = payload.get("role", "")
        user_id = payload.get("sub", "")
        
        if email:
            # Mascarar email para logs
            masked_email = LoggingService._mask_email(email)
            if role:
                return f"{masked_email} ({role})"
            return masked_email
        elif user_id:
            if role:
                return f"User#{user_id} ({role})"
            return f"User#{user_id}"
        else:
            return "Unknown User"

    def _format_user_info(self, user_context: Dict[str, Any]) -> str:
        """Formata informações do usuário para exibição em logs"""
        if user_context.get("authenticated"):
            return user_context.get("display_name", "Unknown User")
        elif user_context.get("jwt_error"):
            return f"Unauthenticated ({user_context.get('display_name', 'No Token')})"
        else:
            return f"Anonymous ({user_context.get('client_ip', 'unknown IP')})"

    async def _extract_request_data(self, request: Request) -> Dict[str, Any]:
        """Extrai dados relevantes da requisição"""
        # Obter IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Headers relevantes (filtrar sensíveis)
        headers = dict(request.headers)
        filtered_headers = self._filter_sensitive_headers(headers)
        
        # Query parameters
        query_params = dict(request.query_params)
        
        # Informações básicas
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": client_ip,
            "user_agent": headers.get("user-agent", "unknown"),
            "query_params": query_params,
            "headers": filtered_headers
        }
        
        # Tentar capturar body (apenas para métodos que normalmente têm body)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                content_type = headers.get("content-type", "")
                if "application/json" in content_type:
                    # Para JSON, capturar o body (cuidado com dados sensíveis)
                    body = await self._get_request_body(request)
                    if body:
                        request_data["body_size"] = len(str(body))
                        # Log do body apenas em debug mode
                        if self.logger.logger.isEnabledFor(10):  # DEBUG level
                            request_data["body"] = self._filter_sensitive_data(body)
                else:
                    request_data["body_size"] = await self._get_body_size(request)
            except Exception:
                request_data["body_size"] = "unknown"
        
        return request_data

    def _extract_response_data(self, response: Response, process_time: float) -> Dict[str, Any]:
        """Extrai dados relevantes da resposta"""
        return {
            "status_code": response.status_code,
            "duration_ms": round(process_time, 2),
            "headers": dict(response.headers)
        }

    def _get_client_ip(self, request: Request) -> str:
        """Obtém o IP real do cliente considerando proxies"""
        # Verificar headers de proxy primeiro
        for header in ["x-forwarded-for", "x-real-ip", "x-client-ip"]:
            if header in request.headers:
                ip = request.headers[header].split(",")[0].strip()
                if ip:
                    return ip
        
        # Fallback para o IP direto
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"

    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove headers sensíveis dos logs"""
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "proxy-authorization", "www-authenticate"
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered[key] = "***MASKED***"
            else:
                filtered[key] = value
                
        return filtered

    def _filter_sensitive_data(self, data: Any) -> Any:
        """Remove dados sensíveis do body da requisição"""
        if isinstance(data, dict):
            sensitive_fields = {"password", "token", "secret", "key", "credential"}
            filtered = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    filtered[key] = "***MASKED***"
                else:
                    filtered[key] = value
            return filtered
        return data

    async def _get_request_body(self, request: Request) -> Any:
        """Obtém o body da requisição de forma segura"""
        try:
            body = await request.body()
            if body:
                return json.loads(body.decode())
        except Exception:
            pass
        return None

    async def _get_body_size(self, request: Request) -> int:
        """Obtém o tamanho do body da requisição"""
        try:
            body = await request.body()
            return len(body)
        except Exception:
            return 0

    def _determine_log_level(self, status_code: int) -> str:
        """Determina o nível de log baseado no status code"""
        if status_code < 400:
            return "info"
        elif status_code < 500:
            return "warning"
        else:
            return "error" 