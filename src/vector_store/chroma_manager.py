import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import json
from datetime import datetime
import os

class ChromaManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Ensure the directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        try:
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            self._initialize_collections()
        except Exception as e:
            print(f"Error initializing ChromaDB: {str(e)}")
            # Try to reinitialize with a clean state
            if os.path.exists(persist_directory):
                import shutil
                shutil.rmtree(persist_directory)
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            self._initialize_collections()

    def _initialize_collections(self):
        """Initialize or get collections for different types of data"""
        try:
            self.dataset_collection = self.client.get_or_create_collection(
                name="datasets"
            )
            self.table_collection = self.client.get_or_create_collection(
                name="tables"
            )
            self.relationship_collection = self.client.get_or_create_collection(
                name="relationships"
            )
        except Exception as e:
            print(f"Error initializing collections: {str(e)}")
            raise

    def save_dataset(self, dataset_name: str, description: str, tables: List[str]):
        """Save dataset information"""
        try:
            metadata = {
                "description": description,
                "tables": json.dumps(tables),
                "created_at": datetime.now().isoformat()
            }
            self.dataset_collection.upsert(
                documents=[description],
                metadatas=[metadata],
                ids=[f"dataset_{dataset_name}"]
            )
        except Exception as e:
            print(f"Error saving dataset: {str(e)}")
            raise

    def save_table_metadata(self, dataset_name: str, table_name: str, 
                          columns: List[Dict], description: str):
        """Save table metadata"""
        try:
            metadata = {
                "dataset_name": dataset_name,
                "columns": json.dumps(columns),
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            self.table_collection.upsert(
                documents=[description],
                metadatas=[metadata],
                ids=[f"table_{dataset_name}_{table_name}"]
            )
        except Exception as e:
            print(f"Error saving table metadata: {str(e)}")
            raise

    def save_relationship(self, dataset_name: str, source_table: str, 
                        target_table: str, join_conditions: List[Dict]):
        """Save table relationships"""
        try:
            metadata = {
                "dataset_name": dataset_name,
                "source_table": source_table,
                "target_table": target_table,
                "join_conditions": json.dumps(join_conditions),
                "created_at": datetime.now().isoformat()
            }
            self.relationship_collection.upsert(
                documents=[f"Join relationship between {source_table} and {target_table}"],
                metadatas=[metadata],
                ids=[f"rel_{dataset_name}_{source_table}_{target_table}"]
            )
        except Exception as e:
            print(f"Error saving relationship: {str(e)}")
            raise

    def get_dataset_info(self, dataset_name: str) -> Optional[Dict]:
        """Retrieve dataset information"""
        try:
            results = self.dataset_collection.get(
                ids=[f"dataset_{dataset_name}"]
            )
            if results and results['metadatas']:
                return results['metadatas'][0]
            return None
        except Exception as e:
            print(f"Error getting dataset info: {str(e)}")
            return None

    def get_table_metadata(self, dataset_name: str, table_name: str) -> Optional[Dict]:
        """Retrieve table metadata"""
        try:
            results = self.table_collection.get(
                ids=[f"table_{dataset_name}_{table_name}"]
            )
            if results and results['metadatas']:
                return results['metadatas'][0]
            return None
        except Exception as e:
            print(f"Error getting table metadata: {str(e)}")
            return None

    def get_relationships(self, dataset_name: str) -> List[Dict]:
        """Retrieve all relationships for a dataset"""
        try:
            results = self.relationship_collection.query(
                query_texts=[""],
                where={"dataset_name": dataset_name}
            )
            return results['metadatas'] if results and results['metadatas'] else []
        except Exception as e:
            print(f"Error getting relationships: {str(e)}")
            return [] 