"""
Knowledge Storage MCP Server.

This module initializes and runs the Knowledge Storage MCP server.
"""

import argparse
import logging
import os
from typing import Optional

import dotenv
from modelcontextprotocol import MCPServer

from knowledge_storage_mcp.api.entities import register_entity_endpoints
from knowledge_storage_mcp.api.relationships import register_relationship_endpoints
from knowledge_storage_mcp.api.queries import register_query_endpoints
from knowledge_storage_mcp.db.connection import Neo4jConnection
from knowledge_storage_mcp.utils.logging import setup_logging

# Load environment variables
dotenv.load_dotenv()

# Set up logging
logger = setup_logging("knowledge_storage_mcp.server")

def create_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    neo4j_uri: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> MCPServer:
    """
    Create and configure the Knowledge Storage MCP server.
    
    Args:
        host: Server host (default: from env or 0.0.0.0)
        port: Server port (default: from env or 8000)
        neo4j_uri: Neo4j URI (default: from env or bolt://localhost:7687)
        neo4j_username: Neo4j username (default: from env or neo4j)
        neo4j_password: Neo4j password (default: from env)
    
    Returns:
        MCPServer: Configured MCP server instance
    """
    # Get configuration from environment variables or parameters
    host = host or os.getenv("MCP_HOST", "0.0.0.0")
    port = port or int(os.getenv("MCP_PORT", "8000"))
    neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username = neo4j_username or os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
    
    if not neo4j_password:
        raise ValueError("Neo4j password must be provided")
    
    # Create Neo4j connection
    db_connection = Neo4jConnection(
        uri=neo4j_uri,
        username=neo4j_username,
        password=neo4j_password,
    )
    
    # Create MCP server
    server = MCPServer(
        name="Knowledge Storage MCP",
        description=(
            "MCP server for storing, retrieving, and querying knowledge entities, "
            "relationships, and their associated metadata extracted from scientific papers."
        ),
        host=host,
        port=port,
    )
    
    # Register API endpoints
    register_entity_endpoints(server, db_connection)
    register_relationship_endpoints(server, db_connection)
    register_query_endpoints(server, db_connection)
    
    logger.info(f"Server configured at {host}:{port}")
    logger.info(f"Connected to Neo4j at {neo4j_uri}")
    
    return server

def main():
    """Run the Knowledge Storage MCP server."""
    parser = argparse.ArgumentParser(description="Knowledge Storage MCP Server")
    parser.add_argument("--host", help="Server host")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--neo4j-uri", help="Neo4j URI")
    parser.add_argument("--neo4j-username", help="Neo4j username")
    parser.add_argument("--neo4j-password", help="Neo4j password")
    args = parser.parse_args()
    
    try:
        server = create_server(
            host=args.host,
            port=args.port,
            neo4j_uri=args.neo4j_uri,
            neo4j_username=args.neo4j_username,
            neo4j_password=args.neo4j_password,
        )
        server.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
