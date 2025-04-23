"""
Knowledge Storage MCP Server

This module serves as the entry point for the Knowledge Storage MCP server.
It initializes the MCP server with the appropriate models, endpoints, and database connections.

The Knowledge Storage MCP provides a central repository for all knowledge entities and relationships
extracted from academic papers, with a focus on maintaining the symbol-concept separation principle.
"""

import os
import logging
from typing import Dict, Any, List, Optional

# MCP SDK imports
from modelcontextprotocol import (
    MCPServer,
    MCPFunction,
    MCPFunctionParameter,
    MCPRequest,
    MCPResponse
)

# Local imports
from knowledge_storage_mcp.db.connection import get_db_connection, initialize_db
from knowledge_storage_mcp.api.entities import register_entity_endpoints
from knowledge_storage_mcp.api.relationships import register_relationship_endpoints
from knowledge_storage_mcp.api.queries import register_query_endpoints
from knowledge_storage_mcp.utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

def create_mcp_server() -> MCPServer:
    """
    Create and configure the Model Context Protocol server for Knowledge Storage.
    
    This function initializes the MCP server with the appropriate endpoints,
    connects to the Neo4j database, and sets up the necessary models and schemas.
    
    Returns:
        MCPServer: The configured MCP server instance
    """
    logger.info("Initializing Knowledge Storage MCP server")
    
    # Initialize the MCP server
    server = MCPServer(
        name="knowledge-storage-mcp",
        description="Knowledge Storage MCP for the Knowledge Extraction System",
        version="0.1.0"
    )
    
    # Initialize database connection
    try:
        db_connection = get_db_connection()
        initialize_db(db_connection)
        logger.info("Successfully connected to Neo4j database")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j database: {str(e)}")
        raise
    
    # Register API endpoints
    register_entity_endpoints(server, db_connection)
    register_relationship_endpoints(server, db_connection)
    register_query_endpoints(server, db_connection)
    
    # Register health check endpoint
    @server.register_function(
        name="health",
        description="Health check for the Knowledge Storage MCP",
        parameters=[]
    )
    async def health_check() -> Dict[str, Any]:
        """
        Simple health check endpoint to verify the server is running.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        return {
            "status": "healthy",
            "database_connected": db_connection.is_connected(),
            "version": "0.1.0"
        }
    
    logger.info("Knowledge Storage MCP server initialized successfully")
    return server

def main():
    """
    Main entry point for the Knowledge Storage MCP server.
    
    This function creates and starts the MCP server.
    """
    # Get configuration from environment
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    # Create the MCP server
    server = create_mcp_server()
    
    # Start the server
    logger.info(f"Starting Knowledge Storage MCP server on {host}:{port}")
    server.start(host=host, port=port)

if __name__ == "__main__":
    main()
