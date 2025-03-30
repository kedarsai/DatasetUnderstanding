from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional, Any, Tuple
import pandas as pd

class DatabaseConnection:
    def __init__(self, connection_string: str):
        """Initialize database connection"""
        self.connection_string = connection_string
        self.engine = None
        self.inspector = None
        self.metadata = None
        self.current_database = None
        self.current_server = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            # For SQL Server with Windows Authentication
            if "mssql" in self.connection_string.lower():
                self.engine = create_engine(
                    self.connection_string,
                    connect_args={"TrustServerCertificate": "yes"}
                )
            else:
                self.engine = create_engine(self.connection_string)
            
            self.inspector = inspect(self.engine)
            self.metadata = MetaData()
            
            # Get current database and server information
            with self.engine.connect() as connection:
                # Get current database
                result = connection.execute(text("SELECT DB_NAME()")).scalar()
                self.current_database = result
                
                # Get server name
                result = connection.execute(text("SELECT @@SERVERNAME")).scalar()
                self.current_server = result
                
            return True
        except SQLAlchemyError as e:
            print(f"Error connecting to database: {str(e)}")
            return False

    def verify_connection(self) -> Tuple[bool, str]:
        """
        Verify the current database connection and return connection details
        
        Returns:
            Tuple[bool, str]: (is_connected, connection_info)
        """
        try:
            if not self.engine:
                return False, "No database engine available"
                
            with self.engine.connect() as connection:
                # Get current database
                current_db = connection.execute(text("SELECT DB_NAME()")).scalar()
                # Get server name
                server_name = connection.execute(text("SELECT @@SERVERNAME")).scalar()
                # Get user name
                user_name = connection.execute(text("SELECT SYSTEM_USER")).scalar()
                
                connection_info = f"""
                Connected to:
                - Server: {server_name}
                - Database: {current_db}
                - User: {user_name}
                """
                return True, connection_info
        except Exception as e:
            return False, f"Connection verification failed: {str(e)}"

    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        try:
            return self.inspector.get_table_names()
        except Exception as e:
            print(f"Error getting tables: {str(e)}")
            return []

    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Get column information for a table"""
        try:
            columns = self.inspector.get_columns(table_name)
            return [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True)
                }
                for col in columns
            ]
        except Exception as e:
            print(f"Error getting columns for table {table_name}: {str(e)}")
            return []

    def get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns for a specific table"""
        if not self.inspector:
            return []
        return self.inspector.get_pk_constraint(table_name)['constrained_columns']

    def get_foreign_keys(self, table_name: str) -> List[Dict]:
        """Get foreign key relationships for a specific table"""
        if not self.inspector:
            return []
        return self.inspector.get_foreign_keys(table_name)

    def get_table_sample(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get a sample of records from a table"""
        try:
            return pd.read_sql(f"SELECT * FROM {table_name} LIMIT {limit}", self.engine)
        except SQLAlchemyError as e:
            print(f"Error getting sample data: {str(e)}")
            return pd.DataFrame()

    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Execute a SQL query and return results as a DataFrame
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame containing query results, or None if query failed
        """
        try:
            # Verify connection before executing query
            is_connected, connection_info = self.verify_connection()
            if not is_connected:
                raise Exception(f"Database connection verification failed: {connection_info}")
            
            # Clean up the query
            query = query.replace("```sql", "").replace("```", "").strip()
            
            # For SELECT queries, use pandas read_sql
            if query.upper().startswith("SELECT"):
                return pd.read_sql(query, self.engine)
            else:
                # For non-SELECT queries, use SQLAlchemy execution
                with self.engine.begin() as connection:
                    # For CREATE VIEW, we need to handle it specially
                    if query.upper().startswith("CREATE VIEW"):
                        # Remove any trailing semicolon
                        query = query.rstrip(';')
                        # Execute the CREATE VIEW statement
                        connection.execute(text(query))
                        # Verify the view was created
                        view_name = query.split()[2]  # Get view name from CREATE VIEW statement
                        verify_query = f"SELECT OBJECT_ID('{view_name}') as view_id"
                        result = connection.execute(text(verify_query)).scalar()
                        if result is None:
                            raise Exception(f"Failed to create view: {view_name}")
                    else:
                        connection.execute(text(query))
                return None
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise

    def close(self):
        """Close the database connection"""
        if self.engine:
            self.engine.dispose() 