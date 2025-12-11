from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# Get the backend directory (parent of app/)
BACKEND_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Databricks Configuration
    databricks_host: str
    databricks_token: str
    databricks_http_path: str
    
    # OMOP Database Configuration
    omop_catalog: str = "hive_metastore"
    omop_schema: str = "omop_cdm"
    
    # GenAI Configuration
    databricks_genie_space_id: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # SSL Configuration (for development/corporate proxies)
    # Set to False to disable SSL verification (NOT recommended for production)
    databricks_verify_ssl: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def omop_full_schema(self) -> str:
        """Get the fully qualified OMOP schema name."""
        return f"{self.omop_catalog}.{self.omop_schema}"
    
    class Config:
        # Use absolute path to .env file in backend directory
        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = False


settings = Settings()

