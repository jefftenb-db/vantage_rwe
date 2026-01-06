from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from pathlib import Path
from app.config import settings
from app.api.routes import router
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vantage RWE API",
    description="Commercial Intelligence from Real-World Evidence - API for pharmaceutical commercial analytics using OHDSI OMOP Common Data Model",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
# Note: FastAPI's allow_origins does not support wildcards (e.g., https://*.databricks.com)
# For wildcard patterns, we use allow_origin_regex instead
cors_config = {
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Add exact origins if any
if settings.cors_origins_list:
    cors_config["allow_origins"] = settings.cors_origins_list

# Add regex pattern for wildcard origins (e.g., Databricks Apps URLs)
if settings.cors_origin_regex:
    cors_config["allow_origin_regex"] = settings.cors_origin_regex

app.add_middleware(CORSMiddleware, **cors_config)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    logger.info(f">>> Incoming request: {request.method} {request.url.path}")
    logger.info(f">>> Client: {request.client}")
    logger.info(f">>> Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"<<< Response status: {response.status_code} (took {process_time:.3f}s)")
        return response
    except Exception as e:
        logger.error(f"!!! Request failed: {e}", exc_info=True)
        raise

# Include API routes
app.include_router(router, prefix="/api/v1")

# Health check endpoints (defined early so they're not caught by catch-all)
@app.get("/health")
async def health():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "Vantage RWE API"}

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for Databricks Apps monitoring."""
    logger.info("Metrics endpoint called")
    return {"status": "ok", "ready": True}

@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {
        "service": "Vantage RWE API",
        "tagline": "Commercial Intelligence from Real-World Evidence",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Get the frontend build directory
FRONTEND_BUILD_DIR = Path(__file__).parent.parent.parent / "frontend" / "build"

# Serve static files from React build (if available)
if FRONTEND_BUILD_DIR.exists():
    logger.info(f"Serving static files from: {FRONTEND_BUILD_DIR}")
    
    # Serve the root index.html explicitly
    @app.get("/")
    async def root():
        """Serve the React app root."""
        logger.info("Serving root / endpoint")
        index_file = FRONTEND_BUILD_DIR / "index.html"
        logger.info(f"Looking for index.html at: {index_file}")
        logger.info(f"Index file exists: {index_file.exists()}")
        if index_file.exists():
            return FileResponse(index_file)
        logger.error(f"index.html not found at {index_file}")
        return {"error": "index.html not found", "path": str(index_file)}
    
    # Mount static files (css, js, images, etc.)
    app.mount("/static", StaticFiles(directory=FRONTEND_BUILD_DIR / "static"), name="static")
    
    # Serve favicon and manifest
    @app.get("/favicon.ico")
    async def favicon():
        favicon_file = FRONTEND_BUILD_DIR / "favicon.ico"
        if favicon_file.exists():
            return FileResponse(favicon_file)
        return {"error": "favicon not found"}
    
    @app.get("/manifest.json")
    async def manifest():
        manifest_file = FRONTEND_BUILD_DIR / "manifest.json"
        if manifest_file.exists():
            return FileResponse(manifest_file)
        return {"error": "manifest not found"}
    
    # Catch-all route to serve React app (must be last)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve the React app for all non-API routes."""
        # Don't intercept API calls, docs, or health checks
        if full_path.startswith(("api/", "api", "docs", "redoc", "health")):
            return {"error": "Not found"}
        
        # Check if a specific file is requested
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise serve index.html (React will handle routing)
        index_file = FRONTEND_BUILD_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "index.html not found"}
else:
    logger.warning(f"Frontend build directory not found at: {FRONTEND_BUILD_DIR}")
    logger.warning("Run 'npm run build' to create the production build")
    
    # If no frontend, serve a simple root endpoint
    @app.get("/")
    async def root_no_frontend():
        """Root endpoint when no frontend is available."""
        return {
            "service": "Vantage RWE API",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/health",
            "note": "Frontend not built - run 'npm run build'"
        }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    try:
        logger.info("=" * 60)
        logger.info("Starting Vantage RWE API")
        logger.info("=" * 60)
        
        # Log configuration
        logger.info(f"API Host: {settings.api_host}")
        logger.info(f"API Port: {settings.api_port}")
        logger.info(f"OMOP Schema: {settings.omop_full_schema}")
        logger.info(f"Databricks Host: {settings.databricks_host}")
        
        # Log CORS configuration
        if settings.cors_origins_list:
            logger.info(f"CORS Exact Origins: {settings.cors_origins_list}")
        if settings.cors_origin_regex:
            logger.info(f"CORS Regex Pattern: {settings.cors_origin_regex}")
        
        # Log frontend status
        frontend_status = "available" if FRONTEND_BUILD_DIR.exists() else "not found"
        logger.info(f"Frontend build: {frontend_status}")
        
        logger.info("=" * 60)
        logger.info("✓ Startup complete - API is ready")
        logger.info("  Health check: /health")
        logger.info("  API docs: /docs")
        logger.info("  API root: /api/v1")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        # Don't crash - allow the app to start even if there are config issues
        logger.warning("Continuing startup despite errors...")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Vantage RWE API")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

