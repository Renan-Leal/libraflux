import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica o token JWT e retorna o usuário atual.
    Esta função decodifica o token JWT e verifica sua validade, retornando os dados do usuário.
    Se o token for inválido ou expirado, uma exceção HTTP 401 é levantada.
    """
    token = credentials.credentials
    secret = os.environ.get("JWT_SECRET_KEY", "")
    jwt_algorithm = os.environ.get("JWT_ALGORITHM", "")
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[jwt_algorithm],
            options={"verify_exp": True},  # Garantir que verifica expiração
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
