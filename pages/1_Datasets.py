import streamlit as st
import pandas as pd
from src.database.connection import DatabaseConnection

# Initialize session state
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None

def main():
    st.title("Datasets")
    
    # Add home button
    if st.button("← Home"):
        st.switch_page("app.py")
    
    # Database connection section
    st.subheader("Database Connection")
    
    if not st.session_state.db_connection:
        db_type = st.selectbox(
            "Database Type",
            ["mssql", "postgresql", "mysql", "sqlite"]
        )
        
        if db_type == "mssql":
            st.info("Using Windows Authentication for SQL Server")
            server = st.text_input("Server Name", "localhost")
            database = st.text_input("Database Name")
            
            if st.button("Connect"):
                try:
                    connection_string = f"mssql+pyodbc://{server}/{database}?driver=SQL+Server+Native+Client+11.0&trusted_connection=yes"
                    st.session_state.db_connection = DatabaseConnection(connection_string)
                    st.session_state.db_connection.connect()
                    st.success("Successfully connected to the database!")
                except Exception as e:
                    st.error(f"Failed to connect to database: {str(e)}")
        else:
            server = st.text_input("Server Name")
            database = st.text_input("Database Name") 
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Connect"):
                try:
                    st.session_state.db_connection = DatabaseConnection(
                        server=server,
                        database=database,
                        username=username,
                        password=password
                    )
                    st.session_state.db_connection.connect()
                    st.success("Successfully connected to the database!")
                except Exception as e:
                    st.error(f"Failed to connect to database: {str(e)}")
    else:
        # Show connection info
        is_connected, connection_info = st.session_state.db_connection.verify_connection()
        if is_connected:
            st.info(connection_info)
            if st.button("Disconnect"):
                st.session_state.db_connection.close()
                st.session_state.db_connection = None
                st.rerun()
        else:
            st.error(f"Connection verification failed: {connection_info}")
            st.session_state.db_connection = None
    
    # Create new dataset button
    if st.session_state.db_connection:
        st.markdown("---")
        if st.button("Create New Dataset"):
            st.switch_page("pages/2_Create_Dataset.py")
    
    # List existing datasets
    if st.session_state.db_connection:
        st.markdown("---")
        st.subheader("Existing Datasets")
        
        try:
            # Query to get all datasets
            query = """
            SELECT 
                DatasetID,
                DatasetName,
                Description,
                CreatedDate,
                CreatedBy,
                ViewName,
                JoinConditions,
                Tables,
                DatabaseName,
                ServerName
            FROM DU_Datasets
            ORDER BY CreatedDate DESC
            """
            
            datasets_df = st.session_state.db_connection.execute_query(query)
            
            if datasets_df is not None and not datasets_df.empty:
                # Add actions column
                datasets_df['Actions'] = ''
                
                # Display datasets in a table with actions
                for index, row in datasets_df.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{row['DatasetName']}**")
                        st.write(f"Description: {row['Description']}")
                        st.write(f"Created: {row['CreatedDate']}")
                        st.write(f"View: {row['ViewName']}")
                        st.markdown("---")
                    
                    with col2:
                        if st.button("View Sample", key=f"sample_{index}"):
                            sample_query = f"SELECT TOP 5 * FROM {row['ViewName']}"
                            sample_data = st.session_state.db_connection.execute_query(sample_query)
                            if sample_data is not None:
                                st.dataframe(sample_data)
                    
                    with col3:
                        if st.button("Profile", key=f"profile_{index}"):
                            st.session_state.profile_view_name = row['ViewName']
                            st.switch_page("pages/3_Dataset_Profiling.py")
            else:
                st.info("No datasets found. Create a new dataset to get started!")
        except Exception as e:
            st.error(f"Error fetching datasets: {str(e)}")

if __name__ == "__main__":
    main()