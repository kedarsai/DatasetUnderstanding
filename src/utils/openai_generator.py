import openai
from typing import List, Dict

class OpenAIGenerator:
    def __init__(self, api_key: str):
        """Initialize OpenAI client"""
        self.client = openai.OpenAI(api_key=api_key)

    def generate_create_view_query(
        self,
        view_name: str,
        tables: List[str],
        table_columns: Dict[str, List[Dict]],
        join_conditions: str
    ) -> str:
        """
        Generate CREATE VIEW query using OpenAI API
        
        Args:
            view_name: Name of the view to create
            tables: List of table names
            table_columns: Dictionary of table columns
            join_conditions: Natural language description of join conditions
            
        Returns:
            str: Generated CREATE VIEW query
        """
        # Prepare the prompt
        prompt = f"""
        Generate a SQL CREATE VIEW statement based on the following information:
        
        View Name: {view_name}
        Tables: {', '.join(tables)}
        
        Table Columns:
        {self._format_table_columns(table_columns)}
        
        Join Conditions: {join_conditions}
        
        Please generate a complete CREATE VIEW statement that:
        1. Uses appropriate table aliases
        2. Includes all relevant columns from both tables
        3. Implements the join conditions as described
        4. Uses proper SQL syntax for SQL Server
        5. Includes appropriate column aliases to avoid name conflicts
        
        Return only the SQL query without any explanations or markdown formatting.
        """
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate only the SQL query without any explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Extract and clean the query
        query = response.choices[0].message.content.strip()
        return query

    def _format_table_columns(self, table_columns: Dict[str, List[Dict]]) -> str:
        """Format table columns for the prompt"""
        formatted = ""
        for table, columns in table_columns.items():
            formatted += f"\n{table}:\n"
            for col in columns:
                formatted += f"  - {col['name']} ({col['type']})\n"
        return formatted 