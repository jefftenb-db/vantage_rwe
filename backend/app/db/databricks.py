from databricks import sql
from typing import List, Dict, Any, Optional
import logging
from contextlib import contextmanager
from app.config import settings
import ssl
import os

logger = logging.getLogger(__name__)

# Disable SSL warnings for unverified HTTPS requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DatabricksConnection:
    """Manages connections to Databricks SQL."""
    
    def __init__(self):
        self.host = settings.databricks_host
        self.token = settings.databricks_token
        self.http_path = settings.databricks_http_path
        self.verify_ssl = settings.databricks_verify_ssl
    
    @contextmanager
    def get_connection(self):
        """Context manager for Databricks SQL connection."""
        connection = None
        
        # Store original SSL settings
        original_ssl_verify = os.environ.get('CURL_CA_BUNDLE')
        original_requests_verify = os.environ.get('REQUESTS_CA_BUNDLE')
        original_context = None
        
        try:
            # Disable SSL verification at the environment level if configured
            if not self.verify_ssl:
                logger.warning("SSL verification is disabled - NOT recommended for production!")
                # Disable SSL verification for requests/urllib3
                os.environ['CURL_CA_BUNDLE'] = ''
                os.environ['REQUESTS_CA_BUNDLE'] = ''
                # Monkey patch ssl for this connection
                import ssl
                original_context = ssl._create_default_https_context
                ssl._create_default_https_context = ssl._create_unverified_context
            
            # Configure connection parameters
            conn_params = {
                "server_hostname": self.host,
                "http_path": self.http_path,
                "access_token": self.token
            }
            
            # Add SSL verification parameters for databricks connector
            if not self.verify_ssl:
                conn_params["_tls_no_verify"] = True
            
            logger.info(f"Connecting to Databricks: {self.host}")
            connection = sql.connect(**conn_params)
            
            yield connection
            
        except Exception as e:
            logger.error(f"Error connecting to Databricks: {e}")
            raise
        finally:
            # Restore SSL context AFTER the connection is used
            if original_context is not None:
                ssl._create_default_https_context = original_context
            
            # Restore original environment variables
            if original_ssl_verify is not None:
                os.environ['CURL_CA_BUNDLE'] = original_ssl_verify
            elif 'CURL_CA_BUNDLE' in os.environ:
                del os.environ['CURL_CA_BUNDLE']
                
            if original_requests_verify is not None:
                os.environ['REQUESTS_CA_BUNDLE'] = original_requests_verify
            elif 'REQUESTS_CA_BUNDLE' in os.environ:
                del os.environ['REQUESTS_CA_BUNDLE']
            
            if connection:
                connection.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                logger.info(f"Executing query: {query}")
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                # Fetch column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Fetch all rows
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                logger.info(f"Query returned {len(results)} rows")
                return results
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_scalar(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query and return a single scalar value."""
        print(f"Executing scalar query: {query}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchone()
                return result[0] if result else None
            except Exception as e:
                logger.error(f"Error executing scalar query: {e}")
                raise
            finally:
                cursor.close()


# Singleton instance
db = DatabricksConnection()

