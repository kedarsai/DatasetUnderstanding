import streamlit as st
import time
import importlib
import sys
from src.config import OPENAI_API_KEY

# Force reload the database module
if 'src.database' in sys.modules:
    importlib.reload(sys.modules['src.database'])
    importlib.reload(sys.modules['src.database.connection'])

from src.database.connection import DatabaseConnection
from src.vector_store.chroma_manager import ChromaManager
from src.utils.join_parser import JoinParser
from src.utils.openai_generator import OpenAIGenerator
import json

# Add a small delay to ensure proper module loading
time.sleep(0.1)

# Initialize session state
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'selected_tables' not in st.session_state:
    st.session_state.selected_tables = []
if 'chroma_manager' not in st.session_state:
    st.session_state.chroma_manager = ChromaManager()
if 'num_table_inputs' not in st.session_state:
    st.session_state.num_table_inputs = 1
if 'table_to_remove' not in st.session_state:
    st.session_state.table_to_remove = None
if 'table_inputs' not in st.session_state:
    st.session_state.table_inputs = [""]
if 'create_view_query' not in st.session_state:
    st.session_state.create_view_query = None
if 'view_name' not in st.session_state:
    st.session_state.view_name = None



def connect_to_database():
    """Establish database connection"""
    if st.session_state.db_type == "mssql":
        # SQL Server with Windows Authentication
        connection_string = f"mssql+pyodbc://{st.session_state.host}/{st.session_state.database}?driver=SQL+Server+Native+Client+11.0&trusted_connection=yes"
    else:
        connection_string = f"{st.session_state.db_type}://{st.session_state.username}:{st.session_state.password}@{st.session_state.host}:{st.session_state.port}/{st.session_state.database}"
    
    db = DatabaseConnection(connection_string)
    if db.connect():
        st.session_state.db_connection = db
        # Verify and display connection information
        is_connected, connection_info = db.verify_connection()
        if is_connected:
            st.success("Successfully connected to database!")
            st.info(connection_info)
        else:
            st.error(f"Connection verification failed: {connection_info}")
        return True
    else:
        st.error("Failed to connect to database. Please check your credentials.")
        return False

def add_table_input():
    """Add a new table input field"""
    st.session_state.num_table_inputs += 1
    st.session_state.table_inputs.append("")

def validate_table_exists(table_name: str) -> bool:
    """Check if the table exists in the database"""
    available_tables = st.session_state.db_connection.get_tables()
    return table_name in available_tables

def sync_table_inputs():
    """Ensure table_inputs list matches num_table_inputs"""
    while len(st.session_state.table_inputs) < st.session_state.num_table_inputs:
        st.session_state.table_inputs.append("")
    while len(st.session_state.table_inputs) > st.session_state.num_table_inputs:
        st.session_state.table_inputs.pop()

def main():
    st.title("SQL Integration Tool")
    
    # Welcome message
    st.markdown("""
    ## Welcome to SQL Integration Tool
    
    This tool helps you create and manage datasets by combining multiple database tables using natural language join conditions.
    
    ### Features:
    - Create new datasets from multiple tables
    - Define join conditions in natural language
    - View and manage existing datasets
    - Sample data preview for datasets
    
    ### Getting Started:
    1. Click the button below to go to the Datasets page
    2. Connect to your database
    3. Create new datasets or view existing ones
    """)
    
    # Navigation button
    if st.button("Go to Datasets"):
        st.switch_page("pages/1_Datasets.py")

if __name__ == "__main__":
    main() 