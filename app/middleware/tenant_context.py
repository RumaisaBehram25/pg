"""Middleware to extract and set tenant context from JWT token."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import jwt, JWTError
from app.core.config import settings


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Extract tenant_id and user_id from JWT token and set in request.state.
    
    This middleware runs BEFORE any endpoint handlers, allowing:
    1. get_db() to access request.state.tenant_id for RLS
    2. get_current_user() to validate against database
    
    The middleware extracts data from the JWT but does NOT validate it.
    Validation happens in get_current_user() which queries the database.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Initialize request state
        request.state.tenant_id = None
        request.state.user_id = None
        
        # Try to extract tenant_id from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                # Decode JWT token (basic decode, no validation)
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                
                # Extract and set tenant_id and user_id in request state
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_id = payload.get("user_id")
                
            except JWTError:
                # Invalid token - don't set state, let endpoint handle it
                pass
        
        # Continue to next middleware/endpoint
        response = await call_next(request)
        return response