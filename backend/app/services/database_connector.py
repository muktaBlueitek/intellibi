from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from cryptography.fernet import Fernet
import base64
import hashlib

from app.models.datasource import DataSource, DataSourceType


class DatabaseConnector:
    """Service for connecting to and querying external databases."""
    
    # Connection pool settings
    POOL_SIZE = 5
    MAX_OVERFLOW = 10
    POOL_RECYCLE = 3600  # Recycle connections after 1 hour
    
    def __init__(self):
        """Initialize the database connector."""
        self._engines: Dict[str, Engine] = {}
        self._encryption_key = self._get_encryption_key()
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for password storage."""
        # In production, this should come from environment variables
        key = "intellibi-db-connector-key-change-in-production"
        key_bytes = key.encode()
        # Generate a 32-byte key using SHA256
        return base64.urlsafe_b64encode(hashlib.sha256(key_bytes).digest())
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt password for storage."""
        if not password:
            return ""
        f = Fernet(self._encryption_key)
        return f.encrypt(password.encode()).decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt password for use."""
        if not encrypted_password:
            return ""
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_password.encode()).decode()
    
    def _build_connection_string(
        self,
        db_type: DataSourceType,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str
    ) -> str:
        """Build SQLAlchemy connection string."""
        if db_type == DataSourceType.POSTGRESQL:
            return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        elif db_type == DataSourceType.MYSQL:
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _get_engine_key(self, datasource_id: int) -> str:
        """Get unique key for engine cache."""
        return f"datasource_{datasource_id}"
    
    def create_engine(
        self,
        datasource: DataSource,
        password: Optional[str] = None
    ) -> Engine:
        """Create or get cached database engine with connection pooling."""
        engine_key = self._get_engine_key(datasource.id)
        
        # Return cached engine if exists
        if engine_key in self._engines:
            return self._engines[engine_key]
        
        # Get password (decrypt if stored encrypted)
        db_password = password
        if not db_password and datasource.connection_config:
            encrypted_pwd = datasource.connection_config.get("encrypted_password")
            if encrypted_pwd:
                db_password = self._decrypt_password(encrypted_pwd)
        
        if not db_password:
            raise ValueError("Password is required for database connection")
        
        # Build connection string
        connection_string = self._build_connection_string(
            db_type=datasource.type,
            host=datasource.host or "localhost",
            port=datasource.port or (5432 if datasource.type == DataSourceType.POSTGRESQL else 3306),
            database=datasource.database_name or "",
            username=datasource.username or "",
            password=db_password
        )
        
        # Create engine with connection pooling
        engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.POOL_SIZE,
            max_overflow=self.MAX_OVERFLOW,
            pool_recycle=self.POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before using
            echo=False
        )
        
        # Cache engine
        self._engines[engine_key] = engine
        
        return engine
    
    def test_connection(self, datasource: DataSource, password: Optional[str] = None) -> Dict[str, Any]:
        """Test database connection."""
        try:
            engine = self.create_engine(datasource, password)
            with engine.connect() as conn:
                # Try a simple query
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            return {
                "success": True,
                "message": "Connection successful",
                "database_type": datasource.type.value
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }
    
    @contextmanager
    def get_connection(self, datasource: DataSource, password: Optional[str] = None):
        """Get database connection context manager."""
        engine = self.create_engine(datasource, password)
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(
        self,
        datasource: DataSource,
        query: str,
        password: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a SQL query and return results."""
        try:
            # Add LIMIT if specified and not already present
            if limit and "LIMIT" not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            with self.get_connection(datasource, password) as conn:
                result = conn.execute(text(query))
                
                # Get column names
                columns = list(result.keys())
                
                # Fetch all rows
                rows = result.fetchall()
                
                # Convert to list of dicts
                data = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "success": True,
                    "columns": columns,
                    "data": data,
                    "row_count": len(data),
                    "query": query
                }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Query execution failed"
            }
    
    def execute_query_dataframe(
        self,
        datasource: DataSource,
        query: str,
        password: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Execute a SQL query and return results as pandas DataFrame."""
        try:
            engine = self.create_engine(datasource, password)
            
            # Add LIMIT if specified
            if limit and "LIMIT" not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            raise ValueError(f"Query execution failed: {str(e)}")
    
    def get_tables(self, datasource: DataSource, password: Optional[str] = None) -> List[str]:
        """Get list of tables in the database."""
        try:
            engine = self.create_engine(datasource, password)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            return tables
        except Exception as e:
            raise ValueError(f"Failed to get tables: {str(e)}")
    
    def get_table_schema(
        self,
        datasource: DataSource,
        table_name: str,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        try:
            engine = self.create_engine(datasource, password)
            inspector = inspect(engine)
            
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_primary_keys(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": str(col.get("default", ""))
                    }
                    for col in columns
                ],
                "primary_keys": primary_keys,
                "foreign_keys": [
                    {
                        "name": fk["name"],
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    }
                    for fk in foreign_keys
                ]
            }
        except Exception as e:
            raise ValueError(f"Failed to get table schema: {str(e)}")
    
    def close_connection(self, datasource_id: int):
        """Close and remove connection pool for a datasource."""
        engine_key = self._get_engine_key(datasource_id)
        if engine_key in self._engines:
            engine = self._engines.pop(engine_key)
            engine.dispose()
    
    def close_all_connections(self):
        """Close all connection pools."""
        for engine_key, engine in list(self._engines.items()):
            engine.dispose()
        self._engines.clear()
