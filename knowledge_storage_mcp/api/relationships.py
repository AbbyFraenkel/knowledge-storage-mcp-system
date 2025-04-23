"""
Relationship API endpoints for the Knowledge Storage MCP.

This module provides endpoints for creating, retrieving, updating,
and deleting knowledge relationships in the Neo4j database.
"""

import logging
from typing import Dict, Any, List, Optional

# MCP SDK imports
from modelcontextprotocol import MCPServer, MCPFunction, MCPFunctionParameter

# Local imports
from knowledge_storage_mcp.db.connection import Neo4jConnection
from knowledge_storage_mcp.db.schema import SchemaManager
from knowledge_storage_mcp.utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

def register_relationship_endpoints(server: MCPServer, db_connection: Neo4jConnection) -> None:
    """
    Register relationship API endpoints with the MCP server.
    
    Args:
        server (MCPServer): The MCP server instance
        db_connection (Neo4jConnection): Database connection instance
    """
    logger.info("Registering relationship API endpoints")
    schema_manager = SchemaManager(db_connection)
    
    @server.register_function(
        name="create_relationship",
        description="Create a relationship between two entities in the knowledge graph",
        parameters=[
            MCPFunctionParameter(
                name="from_entity_id",
                description="Source entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="relationship_type",
                description="Type of relationship (e.g., 'REPRESENTS', 'RELATES_TO')",
                required=True
            ),
            MCPFunctionParameter(
                name="to_entity_id",
                description="Target entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="properties",
                description="Relationship properties following the schema for the relationship type",
                required=False
            )
        ]
    )
    async def create_relationship(from_entity_id: str, relationship_type: str,
                                to_entity_id: str,
                                properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a relationship between two entities in the knowledge graph.
        
        Args:
            from_entity_id (str): Source entity identifier
            relationship_type (str): Type of relationship 
            to_entity_id (str): Target entity identifier
            properties (Optional[Dict[str, Any]]): Relationship properties
        
        Returns:
            Dict[str, Any]: Created relationship information
        """
        logger.info(f"Creating relationship of type '{relationship_type}' from '{from_entity_id}' to '{to_entity_id}'")
        
        try:
            # Validate relationship type and properties
            if properties is None:
                properties = {}
            
            # Check if entities exist
            from_query = "MATCH (e:Entity {id: $id}) RETURN e"
            from_result = db_connection.execute_query(from_query, {"id": from_entity_id})
            
            if not from_result:
                return {
                    "success": False,
                    "message": f"Source entity with ID '{from_entity_id}' not found"
                }
            
            to_query = "MATCH (e:Entity {id: $id}) RETURN e"
            to_result = db_connection.execute_query(to_query, {"id": to_entity_id})
            
            if not to_result:
                return {
                    "success": False,
                    "message": f"Target entity with ID '{to_entity_id}' not found"
                }
            
            # Create relationship
            create_query = f"""
                MATCH (source:Entity {{id: $from_id}}), (target:Entity {{id: $to_id}})
                CREATE (source)-[r:{relationship_type} $properties]->(target)
                RETURN r
            """
            
            params = {
                "from_id": from_entity_id,
                "to_id": to_entity_id,
                "properties": properties
            }
            
            result = db_connection.execute_query(create_query, params)
            
            if not result:
                return {
                    "success": False,
                    "message": "Failed to create relationship"
                }
            
            # Extract relationship from result
            relationship = result[0]["r"]
            
            return {
                "success": True,
                "relationship_type": relationship_type,
                "from_entity_id": from_entity_id,
                "to_entity_id": to_entity_id,
                "properties": properties,
                "message": "Relationship created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create relationship: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to create relationship: {str(e)}"
            }
    
    # Add more relationship endpoints (get, delete, list) here
    
    logger.info("Relationship API endpoints registered")
