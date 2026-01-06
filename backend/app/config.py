from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import re

# Get the backend directory (parent of app/)
BACKEND_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Databricks Configuration
    databricks_host: str
    databricks_http_path: str
    
    # OAuth Service Principal Authentication (required)
    databricks_client_id: str
    databricks_client_secret: str
    
    # OMOP Database Configuration
    omop_catalog: str = "hive_metastore"
    omop_schema: str = "omop_cdm"
    
    # GenAI Configuration
    databricks_genie_space_id: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000  # Databricks Apps default port
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # SSL Configuration (for development/corporate proxies)
    # Set to False to disable SSL verification (NOT recommended for production)
    databricks_verify_ssl: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list, excluding wildcard patterns."""
        origins = []
        for origin in self.cors_origins.split(","):
            origin = origin.strip()
            # Only include exact origins (no wildcards)
            if "*" not in origin:
                origins.append(origin)
        return origins
    
    @property
    def cors_origin_regex(self) -> Optional[str]:
        """
        Generate regex pattern for CORS origins containing wildcards.
        Converts patterns like 'https://*.databricks.com' to proper regex.
        """
        regex_patterns = []
        for origin in self.cors_origins.split(","):
            origin = origin.strip()
            if "*" in origin:
                # Convert wildcard pattern to regex
                # Escape special regex characters except *
                pattern = re.escape(origin).replace(r"\*", ".*")
                regex_patterns.append(pattern)
        
        if regex_patterns:
            # Combine all patterns with OR (|) and add anchors
            return "^(" + "|".join(regex_patterns) + ")$"
        return None
    
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

