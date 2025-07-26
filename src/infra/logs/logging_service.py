import logging
import json
import uuid
from datetime import datetime
from nest.core import Injectable
import colorlog
import os
from typing import Dict, Any, Optional


@Injectable
class LoggingService:
    def __init__(self, file_name: str):
        self.logger_name = file_name
        self.correlation_id = None
        
        # Configurar logger
        self.logger = colorlog.getLogger(file_name)
        self.logger.setLevel(logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO)
        
        # Evitar duplicação de handlers
        if not self.logger.hasHandlers():
            self._setup_handlers()

    def _setup_handlers(self):
        """Configura os handlers para console e arquivo"""
        
        # Handler para console (colorido)
        console_handler = colorlog.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green", 
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(console_formatter)
        
        # Handler para arquivo (JSON estruturado)
        log_file = f"logs/{self.logger_name}/{datetime.now().strftime('%Y-%m-%d')}.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(message)s')  # Só a mensagem JSON
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def set_correlation_id(self, correlation_id: str):
        """Define o correlation ID para esta instância do logger"""
        self.correlation_id = correlation_id

    def _create_structured_log(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Cria log estruturado em formato JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": self.logger_name,
            "correlation_id": self.correlation_id or "no-correlation-id",
            "message": message
        }
        
        # Adicionar dados extras se fornecidos
        if kwargs:
            log_entry.update(kwargs)
            
        return log_entry

    def _log_structured(self, level: str, message: str, **kwargs):
        """Faz log estruturado tanto no console quanto no arquivo"""
        structured_log = self._create_structured_log(level, message, **kwargs)
        
        # Log simples no console
        getattr(self.logger, level.lower())(message)
        
        # Log estruturado no arquivo
        if self.logger.handlers:
            file_handler = [h for h in self.logger.handlers if isinstance(h, logging.FileHandler)]
            if file_handler:
                file_handler[0].emit(logging.LogRecord(
                    name=self.logger_name,
                    level=getattr(logging, level),
                    pathname="",
                    lineno=0,
                    msg=json.dumps(structured_log, ensure_ascii=False),
                    args=(),
                    exc_info=None
                ))

    def info(self, message: str, **kwargs):
        self._log_structured("INFO", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log_structured("DEBUG", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log_structured("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log_structured("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log_structured("CRITICAL", message, **kwargs)

    # Métodos específicos para diferentes tipos de log
    def log_request(self, method: str, url: str, status_code: int, duration_ms: float, **kwargs):
        """Log específico para requisições HTTP"""
        self.info(
            f"{method} {url} - {status_code} ({duration_ms}ms)",
            operation="http_request",
            request_data={
                "method": method,
                "url": url,
                "status_code": status_code,
                "duration_ms": duration_ms
            },
            **kwargs
        )

    def log_auth_event(self, event: str, user_email: str, success: bool, **kwargs):
        """Log específico para eventos de autenticação"""
        level = "INFO" if success else "WARNING"
        message = f"Auth {event}: {'success' if success else 'failed'} for {self._mask_email(user_email)}"
        
        getattr(self, level.lower())(
            message,
            operation="auth_event",
            auth_data={
                "event": event,
                "user_email": self._mask_email(user_email),
                "success": success
            },
            **kwargs
        )

    def log_business_operation(self, operation: str, result: str, duration_ms: float = None, **kwargs):
        """Log específico para operações de negócio"""
        message = f"Operation {operation}: {result}"
        if duration_ms:
            message += f" ({duration_ms}ms)"
            
        self.info(
            message,
            operation="business_operation",
            business_data={
                "operation": operation,
                "result": result,
                "duration_ms": duration_ms
            },
            **kwargs
        )

    @staticmethod
    def _mask_email(email: str) -> str:
        """Mascara email para logs (mantém primeiros e últimos caracteres)"""
        if "@" not in email:
            return email
        user, domain = email.split("@")
        if len(user) <= 2:
            masked_user = "***"
        else:
            masked_user = user[0] + "***" + user[-1]
        return f"{masked_user}@{domain}"

    @staticmethod
    def generate_correlation_id() -> str:
        """Gera um novo correlation ID"""
        return f"req_{uuid.uuid4().hex[:8]}"
