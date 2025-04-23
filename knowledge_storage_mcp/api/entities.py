"""
Entity API endpoints for the Knowledge Storage MCP.

This module provides endpoints for creating, retrieving, updating,
and deleting knowledge entities in the Neo4j database.
"""

import uuid
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

# Default page size for list operations
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

def register_entity_endpoints(server: MCPServer, db_connection: Neo4jConnection) -> None:
    """
    Register entity API endpoints with the MCP server.
    
    Args:
        server (MCPServer): The MCP server instance
        db_connection (Neo4jConnection): Database connection instance
    """
    logger.info("Registering entity API endpoints")
    schema_manager = SchemaManager(db_connection)
    
    @server.register_function(
        name="create_entity",
        description="Create a new entity in the knowledge graph",
        parameters=[
            MCPFunctionParameter(
                name="entity_type",
                description="Type of entity (e.g., 'Concept', 'Symbol')",
                required=True
            ),
            MCPFunctionParameter(
                name="properties",
                description="Entity properties following the schema for the entity type",
                required=True
            ),
            MCPFunctionParameter(
                name="provenance",
                description="Source information and creation metadata",
                required=False
            )
        ]
    )
    async def create_entity(entity_type: str, properties: Dict[str, Any],
                           provenance: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new entity in the knowledge graph.
        
        Args:
            entity_type (Optional[str]): Filter by entity type
            properties (Optional[Dict[str, Any]]): Filter by property values
            page (Optional[int]): Page number (0-based)
            page_size (Optional[int]): Number of results per page
        
        Returns:
            Dict[str, Any]: List of entities matching the filters
        """
        logger.info(f"Listing entities with type='{entity_type}', page={page}, page_size={page_size}")
        
        try:
            # Validate pagination parameters
            if page < 0:
                page = 0
            if page_size <= 0 or page_size > MAX_PAGE_SIZE:
                page_size = DEFAULT_PAGE_SIZE
            
            # Calculate skip value for pagination
            skip = page * page_size
            
            # Start building the query
            query_parts = ["MATCH (e:Entity"]
            params = {}
            
            # Add entity type filter if provided
            if entity_type:
                query_parts[0] += f":{entity_type}"
            
            query_parts[0] += ")"
            
            # Add property filters if provided
            if properties:
                where_clauses = []
                for key, value in properties.items():
                    param_key = f"prop_{key}"
                    where_clauses.append(f"e.{key} = ${param_key}")
                    params[param_key] = value
                
                if where_clauses:
                    query_parts.append("WHERE " + " AND ".join(where_clauses))
            
            # Add pagination
            count_query = " ".join(query_parts + ["RETURN count(e) AS count"])
            
            # Add return, skip, and limit
            query_parts.append(f"RETURN e SKIP {skip} LIMIT {page_size}")
            
            # Build the final query
            query = " ".join(query_parts)
            
            # Get total count for pagination
            count_result = db_connection.execute_query(count_query, params)
            total_count = count_result[0]["count"] if count_result else 0
            
            # Execute the main query
            result = db_connection.execute_query(query, params)
            
            # Extract entities from result
            entities = []
            for record in result:
                entity = record["e"]
                entities.append(entity)
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            has_next = page < total_pages - 1
            has_prev = page > 0
            
            return {
                "success": True,
                "entities": entities,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
        except Exception as e:
            logger.error(f"Failed to list entities: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to list entities: {str(e)}"
            }
    
    @server.register_function(
        name="get_entity_by_properties",
        description="Find an entity by its properties",
        parameters=[
            MCPFunctionParameter(
                name="entity_type",
                description="Entity type",
                required=False
            ),
            MCPFunctionParameter(
                name="properties",
                description="Property values to match",
                required=True
            )
        ]
    )
    async def get_entity_by_properties(properties: Dict[str, Any], 
                                      entity_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Find an entity by matching property values.
        
        Args:
            properties (Dict[str, Any]): Property values to match
            entity_type (Optional[str]): Entity type to filter by
        
        Returns:
            Dict[str, Any]: Entity details or error message
        """
        logger.info(f"Finding entity by properties: {properties}")
        
        try:
            # Start building the query
            query_parts = ["MATCH (e:Entity"]
            params = {}
            
            # Add entity type filter if provided
            if entity_type:
                query_parts[0] += f":{entity_type}"
            
            query_parts[0] += ")"
            
            # Add property filters
            where_clauses = []
            for key, value in properties.items():
                param_key = f"prop_{key}"
                where_clauses.append(f"e.{key} = ${param_key}")
                params[param_key] = value
            
            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))
            
            # Add return and limit to 1
            query_parts.append("RETURN e LIMIT 1")
            
            # Build the final query
            query = " ".join(query_parts)
            
            # Execute the query
            result = db_connection.execute_query(query, params)
            
            if not result:
                return {
                    "success": False,
                    "message": "No entity found matching the specified properties"
                }
            
            # Extract entity from result
            entity = result[0]["e"]
            
            return {
                "success": True,
                "entity": entity,
                "entity_id": entity.get("id")
            }
        except Exception as e:
            logger.error(f"Failed to find entity by properties: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find entity by properties: {str(e)}"
            }
    
    logger.info("Entity API endpoints registered")
            entity_type (str): Type of entity (e.g., 'Concept', 'Symbol')
            properties (Dict[str, Any]): Entity properties
            provenance (Optional[Dict[str, Any]]): Source information and creation metadata
        
        Returns:
            Dict[str, Any]: Created entity information
        """
        logger.info(f"Creating entity of type '{entity_type}'")
        
        # Generate ID if not provided
        if "id" not in properties:
            properties["id"] = str(uuid.uuid4())
        
        # Add provenance if provided
        entity_props = {**properties}
        if provenance:
            entity_props["provenance"] = provenance
        
        return {
            "success": True,
            "entity_id": properties["id"],
            "entity_type": entity_type,
            "properties": properties,
            "message": "Entity created successfully"
        }
    
    # Add more entity endpoints (get, update, delete, list) here
    
    logger.info("Entity API endpoints registered")
