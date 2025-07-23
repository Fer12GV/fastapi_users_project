import time
import uuid
import re
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import logger, log_request

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            log_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration
            )

            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Completed {response.status_code} in {duration:.3f}s"
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Failed in {duration:.3f}s: {str(e)}"
            )
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""

    def __init__(self, app):
        super().__init__(app)
        self.docs_path_pattern = re.compile(r"^/(docs|redoc|openapi.json)")

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Headers comunes
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Swagger docs: permitir scripts inline (por requerimientos de Swagger UI)
        if self.docs_path_pattern.match(str(request.url.path)):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
                "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        else:
            # Política más estricta para todo lo demás
            response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response
