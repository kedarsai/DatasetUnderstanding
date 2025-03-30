from typing import List, Dict, Tuple
import re

class JoinParser:
    @staticmethod
    def parse_join_condition(condition_text: str) -> List[Dict]:
        """
        Parse natural language join condition into structured format
        Example input: "Join orders table with customers table using customer_id"
        """
        # Initialize result list
        joins = []
        
        # Split multiple join conditions if they exist
        conditions = [c.strip() for c in condition_text.split(',')]
        
        for condition in conditions:
            # Extract table names and join field
            pattern = r"join\s+(\w+)\s+table\s+with\s+(\w+)\s+table\s+using\s+(\w+)"
            match = re.search(pattern, condition.lower())
            
            if match:
                source_table, target_table, join_field = match.groups()
                
                join_info = {
                    "source_table": source_table,
                    "target_table": target_table,
                    "join_field": join_field,
                    "join_type": "inner"  # Default to inner join
                }
                
                # Check for join type if specified
                if "left" in condition.lower():
                    join_info["join_type"] = "left"
                elif "right" in condition.lower():
                    join_info["join_type"] = "right"
                elif "full" in condition.lower():
                    join_info["join_type"] = "full"
                
                joins.append(join_info)
        
        return joins

    @staticmethod
    def generate_sql_join(joins: List[Dict]) -> str:
        """
        Generate SQL JOIN statement from structured join information
        """
        if not joins:
            return ""
        
        # Start with the first table
        sql = f"FROM {joins[0]['source_table']}"
        
        # Add each join
        for join in joins:
            join_type = join["join_type"].upper()
            sql += f"\n{join_type} JOIN {join['target_table']} "
            sql += f"ON {join['source_table']}.{join['join_field']} = "
            sql += f"{join['target_table']}.{join['join_field']}"
        
        return sql

    @staticmethod
    def validate_join_condition(condition_text: str) -> Tuple[bool, str]:
        """
        Validate if the join condition text is properly formatted
        Returns (is_valid, error_message)
        """
        if not condition_text.strip():
            return False, "Join condition cannot be empty"
        
        # Check for basic structure
        if not all(word in condition_text.lower() for word in ["join", "table", "with", "using"]):
            return False, "Join condition must include 'join', 'table', 'with', and 'using' keywords"
        
        # Check for table names
        table_pattern = r"join\s+(\w+)\s+table\s+with\s+(\w+)\s+table"
        if not re.search(table_pattern, condition_text.lower()):
            return False, "Invalid table name format"
        
        # Check for join field
        field_pattern = r"using\s+(\w+)"
        if not re.search(field_pattern, condition_text.lower()):
            return False, "Invalid join field format"
        
        return True, "" 