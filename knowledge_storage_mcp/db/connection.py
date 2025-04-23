"""
Neo4j Database Connection Module

This module handles the connection to the Neo4j database, including initialization,
connection pooling, and transaction management. It provides a clean interface for
other components to interact with the database.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager

from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import ServiceUnavailable, AuthError

# Local imports
from knowledge_storage_mcp.utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

class Neo4jConnection:
    """
    Neo4j database connection manager.
    
    This class handles the connection to the Neo4j database, including
    connection pooling, session management, and transaction handling.
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize the Neo4j connection.
        
        Args:
            uri (str): Neo4j connection URI
            username (str): Neo4j username
            password (str): Neo4j password
        """
        self._driver = None
        self.uri = uri
        self.username = username
        self.password = password
        self.connect()
    
    def connect(self) -> None:
        """
        Establish connection to the Neo4j database.
        
        Raises:
            ServiceUnavailable: If the Neo4j service is not available
            AuthError: If authentication fails
        """
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            # Verify connection by running a simple query
            with self._driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {self.uri}")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
    
    def is_connected(self) -> bool:
        """
        Check if the connection to Neo4j is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self._driver:
            return False
        
        try:
            with self._driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    @contextmanager
    def session(self) -> Session:
        """
        Get a Neo4j session as a context manager.
        
        Yields:
            Session: Neo4j session
        """
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j")
        
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()
    
    @contextmanager
    def transaction(self) -> Transaction:
        """
        Get a Neo4j transaction as a context manager.
        
        Yields:
            Transaction: Neo4j transaction
        """
        with self.session() as session:
            tx = session.begin_transaction()
            try:
                yield tx
                tx.commit()
            except Exception as e:
                tx.rollback()
                logger.error(f"Transaction rolled back: {str(e)}")
                raise
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.
        
        Args:
            query (str): Cypher query
            parameters (Optional[Dict[str, Any]]): Query parameters
        
        Returns:
            List[Dict[str, Any]]: Query results
        """
        parameters = parameters or {}
        with self.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
    
    def execute_write_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a write query within a transaction.
        
        Args:
            query (str): Cypher query
            parameters (Optional[Dict[str, Any]]): Query parameters
        
        Returns:
            List[Dict[str, Any]]: Query results
        """
        parameters = parameters or {}
        with self.transaction() as tx:
            result = tx.run(query, parameters)
            return [record.data() for record in result]

# Global connection instance
_db_connection = None

def get_db_connection() -> Neo4jConnection:
    """
    Get the Neo4j database connection singleton.
    
    Returns:
        Neo4jConnection: The Neo4j connection instance
    """
    global _db_connection
    
    if _db_connection is None:
        # Get configuration from environment variables
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        username = os.environ.get("NEO4J_USERNAME", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        _db_connection = Neo4jConnection(uri, username, password)
    
    return _db_connection

def initialize_db(connection: Neo4jConnection) -> None:
    """
    Initialize the Neo4j database with constraints and indexes.
    
    This function sets up the necessary constraints and indexes for the
    knowledge graph entities and relationships.
    
    Args:
        connection (Neo4jConnection): The Neo4j connection
    """
    # Create constraints for entity uniqueness
    constraints = [
        "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT symbol_id_unique IF NOT EXISTS FOR (s:Symbol) REQUIRE s.id IS UNIQUE"
    ]
    
    # Create indexes for efficient querying
    indexes = [
        "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name)",
        "CREATE INDEX entity_type_idx IF NOT EXISTS FOR (e:Entity) ON (e.type)",
        "CREATE INDEX concept_domain_idx IF NOT EXISTS FOR (c:Concept) ON (c.domain)"
    ]
    
    try:
        for constraint in constraints:
            connection.execute_write_query(constraint)
            logger.debug(f"Created constraint: {constraint}")
        
        for index in indexes:
            connection.execute_write_query(index)
            logger.debug(f"Created index: {index}")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
