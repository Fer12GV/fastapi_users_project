from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.routers import user_router, health_router

# Setup logging first
setup_logging()

# Create FastAPI app with lifespan events
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG if hasattr(settings, 'DEBUG') else False
)

# Add middleware (order matters - first added = outermost layer)
if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router.router, prefix="/api/v1/users", tags=["users"])
if settings.ENABLE_HEALTH_CHECKS:
    app.include_router(health_router.router, prefix="/api/v1/health", tags=["health"])

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": "/api/v1/health" if settings.ENABLE_HEALTH_CHECKS else "disabled"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}
