import os
import hashlib
import time
from nest.core import Injectable
from .dtos.auth_signup import AuthSignup
from .dtos.auth_login import AuthLogin
from ..user.user import User
from ...infra.repositories.user.user_repository import UserRepository
from ...infra.logs.logging_service import LoggingService
import jwt
import datetime
from typing import Optional, Dict, Any


@Injectable
class AuthService:
    def __init__(self, userRepository: UserRepository, logger: LoggingService = None):
        self.userRepository = userRepository
        self.secret = os.environ.get("JWT_SECRET_KEY", "")
        self.algorithm = os.environ.get("JWT_ALGORITHM", "")
        self.logger = logger or LoggingService("AuthService")

    def set_request_context(self, correlation_id: str, user_context: Dict[str, Any] = None):
        """Define o contexto da requisição para logs mais ricos"""
        self.logger.set_correlation_id(correlation_id)
        self.current_user_context = user_context or {}

    def signup(self, authSignup: AuthSignup, request_context: Dict[str, Any] = None):
        """
        Cria um novo usuário com base nos dados fornecidos.
        
        :param authSignup: Dados do usuário a ser criado.
        :param request_context: Contexto da requisição (IP, user agent, etc.)
        :return: Um dicionário com os detalhes do usuário criado ou uma mensagem de erro.
        """
        start_time = time.time()
        
        # Contexto adicional para logs
        request_info = request_context or {}
        client_ip = request_info.get("client_ip", "unknown")
        user_agent = request_info.get("user_agent", "unknown")
        
        # Log início da operação com contexto do request
        self.logger.info(
            f"Starting user signup for email: {self.logger._mask_email(authSignup.email)}",
            operation="signup_start",
            user_data={
                "email": self.logger._mask_email(authSignup.email),
                "name": authSignup.name,
                "role": authSignup.role if hasattr(authSignup, "role") else "user"
            },
            request_context={
                "client_ip": client_ip,
                "user_agent": user_agent
            }
        )
        
        try:
            # Verificar se usuário já existe
            existing_user = self.userRepository.find_by_email(authSignup.email)
            if existing_user:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.log_auth_event(
                    "signup", 
                    authSignup.email, 
                    False,
                    error_reason="user_already_exists",
                    duration_ms=duration_ms,
                    security_context={
                        "client_ip": client_ip,
                        "attempt_type": "duplicate_registration",
                        "existing_user_id": existing_user.id
                    }
                )
                return {"message": "User already exists"}, 409
            
            # Criar hash da senha
            password_hash = hashlib.sha256(
                (authSignup.password + self.secret).encode()
            ).hexdigest()
            
            # Criar objeto usuário
            user = User(
                authSignup.email,
                authSignup.name,
                password_hash,
                authSignup.role if hasattr(authSignup, "role") else None,
            )
            user_model = user.to_user_model()
            
            # Salvar usuário
            created_user = self.userRepository.save(user_model)
            duration_ms = (time.time() - start_time) * 1000
            
            if created_user:
                self.logger.log_auth_event(
                    "signup", 
                    authSignup.email, 
                    True,
                    user_id=created_user.id,
                    duration_ms=duration_ms,
                    security_context={
                        "client_ip": client_ip,
                        "new_user_role": str(created_user.role),
                        "registration_source": "api"
                    }
                )
                
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
                self.logger.log_auth_event(
                    "signup", 
                    authSignup.email, 
                    False,
                    error_reason="failed_to_save_user",
                    duration_ms=duration_ms,
                    security_context={
                        "client_ip": client_ip,
                        "failure_type": "database_error"
                    }
                )
                return {"message": "Failed to create user"}, 400
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Signup failed for {self.logger._mask_email(authSignup.email)}: {str(e)}",
                operation="signup_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms
                },
                user_data={
                    "email": self.logger._mask_email(authSignup.email)
                },
                security_context={
                    "client_ip": client_ip,
                    "error_category": "system_error"
                }
            )
            return {"message": f"Failed to create user: {str(e)}"}, 400

    def login(self, authLogin: AuthLogin, request_context: Dict[str, Any] = None):
        """
        Realiza o login do usuário com base no email e senha fornecidos.
        
        :param authLogin: Dados de login do usuário.
        :param request_context: Contexto da requisição (IP, user agent, etc.)
        :return: Um dicionário com o token de acesso ou uma mensagem de erro.
        """
        start_time = time.time()
        
        # Contexto adicional para logs de segurança
        request_info = request_context or {}
        client_ip = request_info.get("client_ip", "unknown")
        user_agent = request_info.get("user_agent", "unknown")
        
        # Log início da operação com contexto de segurança
        self.logger.info(
            f"Starting user login for email: {self.logger._mask_email(authLogin.email)}",
            operation="login_start",
            user_data={
                "email": self.logger._mask_email(authLogin.email)
            },
            security_context={
                "client_ip": client_ip,
                "user_agent": user_agent,
                "login_attempt": True
            }
        )
        
        try:
            # Buscar usuário por email
            user = self.userRepository.find_by_email(authLogin.email)
            duration_ms = (time.time() - start_time) * 1000

            if not user:
                self.logger.log_auth_event(
                    "login", 
                    authLogin.email, 
                    False,
                    error_reason="user_not_found",
                    duration_ms=duration_ms,
                    security_context={
                        "client_ip": client_ip,
                        "threat_level": "low",
                        "attack_type": "user_enumeration_attempt"
                    }
                )
                return {"message": "User not found"}, 404

            # Verificar senha
            password_hash = hashlib.sha256(
                (authLogin.password + self.secret).encode()
            ).hexdigest()

            if user.password != password_hash:
                self.logger.log_auth_event(
                    "login", 
                    authLogin.email, 
                    False,
                    error_reason="invalid_password",
                    duration_ms=duration_ms,
                    user_id=user.id,
                    security_context={
                        "client_ip": client_ip,
                        "threat_level": "medium",
                        "attack_type": "brute_force_attempt",
                        "existing_user": True
                    }
                )
                return {"message": "Invalid credentials"}, 401

            # Gerar token JWT
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)

            payload = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "exp": expiration_time,
            }

            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            duration_ms = (time.time() - start_time) * 1000

            # Log sucesso do login com informações de segurança
            self.logger.log_auth_event(
                "login", 
                authLogin.email, 
                True,
                user_id=user.id,
                token_expires_at=expiration_time.isoformat(),
                duration_ms=duration_ms,
                security_context={
                    "client_ip": client_ip,
                    "session_type": "jwt_token",
                    "token_lifetime_hours": 2,
                    "user_role": user.role.value,
                    "login_success": True
                }
            )

            return {"access_token": token, "token_type": "bearer"}, 200
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Login failed for {self.logger._mask_email(authLogin.email)}: {str(e)}",
                operation="login_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms
                },
                user_data={
                    "email": self.logger._mask_email(authLogin.email)
                },
                security_context={
                    "client_ip": client_ip,
                    "error_category": "system_error",
                    "threat_level": "high"
                }
            )
            return {"message": "Internal server error"}, 500
