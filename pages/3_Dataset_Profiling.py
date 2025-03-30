import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def get_column_statistics(df: pd.DataFrame, column: str) -> dict:
    """Calculate basic statistics for a column"""
    stats = {
        'Data Type': str(df[column].dtype),
        'Total Rows': len(df),
        'Null Count': df[column].isnull().sum(),
        'Null Percentage': f"{(df[column].isnull().sum() / len(df) * 100):.2f}%"
    }
    
    # Add numeric statistics if applicable
    if pd.api.types.is_numeric_dtype(df[column]):
        stats.update({
            'Min': df[column].min(),
            'Max': df[column].max(),
            'Mean': df[column].mean(),
            'Median': df[column].median(),
            'Standard Deviation': df[column].std()
        })
    
    # Add unique value count for categorical columns
    if pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_categorical_dtype(df[column]):
        stats['Unique Values'] = df[column].nunique()
    
    return stats

def main():
    st.title("Dataset Profiling")
    
    # Add navigation buttons
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Home"):
            st.switch_page("app.py")
    with col2:
        if st.button("← Back to Datasets"):
            st.switch_page("pages/1_Datasets.py")
    
    # Check if we have the view name in session state
    if 'profile_view_name' not in st.session_state:
        st.error("No dataset selected for profiling. Please go back to the datasets page.")
        return
    
    view_name = st.session_state.profile_view_name
    
    try:
        # Get sample data from the view
        sample_query = f"SELECT TOP 1000 * FROM {view_name}"
        df = st.session_state.db_connection.execute_query(sample_query)
        
        if df is None or df.empty:
            st.error(f"No data found in view: {view_name}")
            return
        
        # Display basic information
        st.subheader(f"View: {view_name}")
        st.write(f"Total Rows: {len(df)}")
        st.write(f"Number of Columns: {len(df.columns)}")
        
        # Create profiling DataFrame
        profiling_data = []
        for column in df.columns:
            stats = get_column_statistics(df, column)
            stats['Column Name'] = column
            profiling_data.append(stats)
        
        profiling_df = pd.DataFrame(profiling_data)
        
        # Display profiling results
        st.subheader("Column-wise Statistics")
        st.dataframe(profiling_df)
        
        # Add download button
        csv = profiling_df.to_csv(index=False)
        st.download_button(
            label="Download Profiling Results as CSV",
            data=csv,
            file_name=f"{view_name}_profiling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Display sample data
        st.subheader("Sample Data")
        st.dataframe(df.head())
        
    except Exception as e:
        st.error(f"Error profiling dataset: {str(e)}")

if __name__ == "__main__":
    main() 