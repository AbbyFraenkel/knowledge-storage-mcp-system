"""
Neo4j database connection for the Knowledge Storage MCP.

This module provides a connection to the Neo4j graph database
for storing and retrieving knowledge entities and relationships.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from neo4j import GraphDatabase, Driver, Session, Result

from knowledge_storage_mcp.utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

class Neo4jConnection:
    """
    Neo4j database connection handler.
    
    This class manages the connection to a Neo4j database and provides
    methods for executing Cypher queries and transactions.
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize the Neo4j connection.
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def get_driver(self) -> Driver:
        """Get the Neo4j driver instance."""
        return self.driver
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            List of query result records as dictionaries
        """
        if parameters is None:
            parameters = {}
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}\nQuery: {query}\nParameters: {parameters}")
            raise
    
    def execute_transaction(self, function, *args, **kwargs) -> Any:
        """
        Execute a function within a transaction.
        
        Args:
            function: Transaction function (receives a transaction object as its first argument)
            *args: Additional positional arguments for the function
            **kwargs: Additional keyword arguments for the function
        
        Returns:
            Result of the transaction function
        """
        try:
            with self.driver.session() as session:
                return session.execute_write(function, *args, **kwargs)
        except Exception as e:
            logger.error(f"Transaction execution failed: {str(e)}")
            raise
    
    def execute_read_transaction(self, function, *args, **kwargs) -> Any:
        """
        Execute a read-only function within a transaction.
        
        Args:
            function: Transaction function (receives a transaction object as its first argument)
            *args: Additional positional arguments for the function
            **kwargs: Additional keyword arguments for the function
        
        Returns:
            Result of the transaction function
        """
        try:
            with self.driver.session() as session:
                return session.execute_read(function, *args, **kwargs)
        except Exception as e:
            logger.error(f"Read transaction execution failed: {str(e)}")
            raise
    
    def create_constraint(self, label: str, property_name: str) -> None:
        """
        Create a uniqueness constraint for a node label and property.
        
        Args:
            label: Node label
            property_name: Property name for the constraint
        """
        try:
            query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
            self.execute_query(query)
            logger.info(f"Created constraint on {label}.{property_name}")
        except Exception as e:
            logger.error(f"Failed to create constraint: {str(e)}")
            raise
    
    def create_index(self, label: str, property_name: str) -> None:
        """
        Create an index for a node label and property.
        
        Args:
            label: Node label
            property_name: Property name for the index
        """
        try:
            query = f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.{property_name})"
            self.execute_query(query)
            logger.info(f"Created index on {label}.{property_name}")
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise
