from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.api.routes import router

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Vantage RWE API")
    logger.info(f"OMOP Schema: {settings.omop_full_schema}")
    logger.info(f"Databricks Host: {settings.databricks_host}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Vantage RWE API")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Vantage RWE API",
        "tagline": "Commercial Intelligence from Real-World Evidence",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

