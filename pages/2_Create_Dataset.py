import streamlit as st
import time
import importlib
import sys
import json
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import OPENAI_API_KEY
from src.database.connection import DatabaseConnection
from src.vector_store.chroma_manager import ChromaManager
from src.utils.openai_generator import OpenAIGenerator

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

def save_dataset_info(dataset_name: str, description: str, join_conditions: str, view_name: str):
    """Save dataset information to DU_Datasets table"""
    try:
        # Get current user and database info
        is_connected, connection_info = st.session_state.db_connection.verify_connection()
        if not is_connected:
            raise Exception("Database connection verification failed")
            
        # Get current user
        user_query = "SELECT SYSTEM_USER"
        current_user = st.session_state.db_connection.execute_query(user_query).iloc[0, 0]
        
        # Get database and server info
        db_query = "SELECT DB_NAME()"
        db_name = st.session_state.db_connection.execute_query(db_query).iloc[0, 0]
        
        server_query = "SELECT @@SERVERNAME"
        server_name = st.session_state.db_connection.execute_query(server_query).iloc[0, 0]
        
        # Prepare insert query
        insert_query = f"""
        INSERT INTO DU_Datasets (
            DatasetName, Description, CreatedBy, ViewName,
            JoinConditions, Tables, DatabaseName, ServerName
        ) VALUES (
            '{dataset_name}',
            '{description}',
            '{current_user}',
            '{view_name}',
            '{join_conditions}',
            '{json.dumps(st.session_state.selected_tables)}',
            '{db_name}',
            '{server_name}'
        )
        """
        
        # Execute insert
        st.session_state.db_connection.execute_query(insert_query)
        return True
    except Exception as e:
        st.error(f"Error saving dataset information: {str(e)}")
        return False

def main():
    st.title("Create New Dataset")
    
    # Add navigation buttons
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Home"):
            st.switch_page("app.py")
    with col2:
        if st.button("← Back to Datasets"):
            st.switch_page("pages/1_Datasets.py")
    
    # Check if database is connected
    if not st.session_state.db_connection:
        st.error("Please connect to the database from the main page first.")
        return
    
    # Dataset information
    dataset_name = st.text_input("Dataset Name")
    dataset_description = st.text_area("Dataset Description")
    
    # Table selection
    st.subheader("Select Tables")
    
    # Ensure table_inputs is synchronized
    sync_table_inputs()
    
    # Table input interface
    for i in range(st.session_state.num_table_inputs):
        col1, col2 = st.columns([3, 1])
        with col1:
            table_name = st.text_input(
                f"Enter Table Name {i+1}",
                key=f"table_{i}",
                value=st.session_state.table_inputs[i]
            )
            st.session_state.table_inputs[i] = table_name
            
            if table_name:
                if validate_table_exists(table_name):
                    if table_name not in st.session_state.selected_tables:
                        st.session_state.selected_tables.append(table_name)
                        st.success(f"Added table: {table_name}")
                        st.rerun()
                else:
                    st.error(f"Table '{table_name}' does not exist in the database")
        
        with col2:
            if i == st.session_state.num_table_inputs - 1:
                if st.button("Add More Tables"):
                    add_table_input()
                    st.rerun()
    
    # Display selected tables with visual separation
    if st.session_state.selected_tables:
        st.markdown("---")  # Add horizontal line
        st.subheader("Selected Tables")
        
        # Create a container with a border
        with st.container():
            st.markdown("""
                <style>
                .selected-tables-container {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 10px 0;
                }
                </style>
                """, unsafe_allow_html=True)
            
            for table in st.session_state.selected_tables:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(table)
                with col2:
                    if st.button("Remove", key=f"remove_{table}"):
                        st.session_state.table_to_remove = table
                        st.rerun()
    
    # Handle table removal after rerun
    if st.session_state.table_to_remove:
        if st.session_state.table_to_remove in st.session_state.selected_tables:
            st.session_state.selected_tables.remove(st.session_state.table_to_remove)
            # Clear the corresponding input field
            for i, input_value in enumerate(st.session_state.table_inputs):
                if input_value == st.session_state.table_to_remove:
                    st.session_state.table_inputs[i] = ""
            st.session_state.table_to_remove = None
            st.rerun()
    
    # Join conditions (only show if multiple tables are selected)
    if len(st.session_state.selected_tables) > 1:
        st.markdown("---")  # Add horizontal line
        st.subheader("Define Join Conditions")
        st.write("Describe how you want to join the tables in natural language. Example: 'Join Employee and Student tables where their names match'")
        join_conditions = st.text_area("Join Conditions")
        
        if st.button("Generate View Definition"):
            try:
                # Get table columns for all selected tables
                table_columns = {}
                for table in st.session_state.selected_tables:
                    table_columns[table] = st.session_state.db_connection.get_table_columns(table)
                
                # Initialize OpenAI generator
                generator = OpenAIGenerator(OPENAI_API_KEY)
                
                # Generate CREATE VIEW query
                st.session_state.view_name = dataset_name  # Use dataset name as view name
                st.session_state.create_view_query = generator.generate_create_view_query(
                    view_name=st.session_state.view_name,
                    tables=st.session_state.selected_tables,
                    table_columns=table_columns,
                    join_conditions=join_conditions
                )
                
                st.code(st.session_state.create_view_query, language="sql")
                
            except Exception as e:
                st.error(f"Error generating view definition: {str(e)}")
        
        # View creation section (only show if we have a generated query)
        if st.session_state.create_view_query:
            st.markdown("---")
            st.subheader("Create View in Database")
            
            # Show current connection information
            is_connected, connection_info = st.session_state.db_connection.verify_connection()
            if is_connected:
                st.info(connection_info)
            else:
                st.error(f"Connection verification failed: {connection_info}")
            
            if st.button("Create View"):
                try:
                    # Execute the CREATE VIEW query
                    st.session_state.db_connection.execute_query(st.session_state.create_view_query)
                    
                    # Save dataset information
                    if save_dataset_info(
                        dataset_name=dataset_name,
                        description=dataset_description,
                        join_conditions=join_conditions,
                        view_name=st.session_state.view_name
                    ):
                        st.success(f"Successfully created view: {st.session_state.view_name}")
                        
                        # Show sample data from the view
                        sample_query = f"SELECT TOP 5 * FROM {st.session_state.view_name}"
                        sample_data = st.session_state.db_connection.execute_query(sample_query)
                        if sample_data is not None:
                            st.subheader("Sample Data from View")
                            st.dataframe(sample_data)
                        
                        # Add button to return to datasets page
                        if st.button("Return to Datasets"):
                            st.switch_page("pages/1_Datasets.py")
                    else:
                        st.error("Failed to save dataset information")
                except Exception as e:
                    st.error(f"Error creating view: {str(e)}")
                    st.error("Please check if you have sufficient permissions to create views in the database.")
    else:
        st.info("Add at least two tables to define join conditions")

if __name__ == "__main__":
    main() 