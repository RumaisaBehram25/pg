from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import jwt, JWTError
from app.core.config import settings


class TenantContextMiddleware(BaseHTTPMiddleware):

    
    async def dispatch(self, request: Request, call_next):
        request.state.tenant_id = None
        request.state.user_id = None
        
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_id = payload.get("user_id")
                
            except JWTError:
                pass
        
        response = await call_next(request)
        return response