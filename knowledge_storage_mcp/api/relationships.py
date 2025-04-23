"""
Relationship API endpoints for the Knowledge Storage MCP.

This module provides endpoints for creating, retrieving, updating,
and deleting knowledge relationships in the Neo4j database.
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
        description="Create a relationship between two entities",
        parameters=[
            MCPFunctionParameter(
                name="source_id",
                description="Source entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="relationship_type",
                description="Type of relationship",
                required=True
            ),
            MCPFunctionParameter(
                name="target_id",
                description="Target entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="properties",
                description="Relationship properties",
                required=False
            )
        ]
    )
    async def create_relationship(source_id: str, relationship_type: str, target_id: str,
                               properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a relationship between two entities.
        
        Args:
            source_id (str): Source entity identifier
            relationship_type (str): Type of relationship
            target_id (str): Target entity identifier
            properties (Optional[Dict[str, Any]]): Relationship properties
        
        Returns:
            Dict[str, Any]: Created relationship information
        """
        logger.info(f"Creating relationship '{relationship_type}' from '{source_id}' to '{target_id}'")
        
        try:
            # Initialize properties if not provided
            properties = properties or {}
            
            # First, check if both entities exist
            query_source = """
            MATCH (source:Entity {id: $source_id})
            RETURN labels(source) AS source_labels
            """
            source_result = db_connection.execute_query(query_source, {"source_id": source_id})
            
            if not source_result:
                return {
                    "success": False,
                    "message": f"Source entity with ID '{source_id}' not found"
                }
            
            query_target = """
            MATCH (target:Entity {id: $target_id})
            RETURN labels(target) AS target_labels
            """
            target_result = db_connection.execute_query(query_target, {"target_id": target_id})
            
            if not target_result:
                return {
                    "success": False,
                    "message": f"Target entity with ID '{target_id}' not found"
                }
            
            # Extract entity types from labels
            source_labels = source_result[0]["source_labels"]
            source_types = [label for label in source_labels if label != "Entity"]
            source_type = source_types[0] if source_types else "Entity"
            
            target_labels = target_result[0]["target_labels"]
            target_types = [label for label in target_labels if label != "Entity"]
            target_type = target_types[0] if target_types else "Entity"
            
            # Validate relationship against schema
            is_valid, errors = schema_manager.validate_relationship(
                relationship_type, source_type, target_type, properties
            )
            
            if not is_valid:
                return {
                    "success": False,
                    "errors": errors,
                    "message": "Relationship validation failed"
                }
            
            # Generate unique identifier for the relationship
            relationship_id = str(uuid.uuid4())
            properties["id"] = relationship_id
            
            # Build property string for Cypher query
            props_string = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            props_clause = f"{{{props_string}}}" if props_string else ""
            
            # Create relationship query
            query = f"""
            MATCH (source:Entity {{id: $source_id}}), (target:Entity {{id: $target_id}})
            CREATE (source)-[r:{relationship_type} {props_clause}]->(target)
            RETURN r
            """
            
            # Prepare query parameters
            params = {**properties, "source_id": source_id, "target_id": target_id}
            
            # Execute query
            result = db_connection.execute_write_query(query, params)
            
            return {
                "success": True,
                "relationship_id": relationship_id,
                "source_id": source_id,
                "relationship_type": relationship_type,
                "target_id": target_id,
                "properties": properties,
                "message": "Relationship created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create relationship: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to create relationship: {str(e)}"
            }
    
    @server.register_function(
        name="get_relationship",
        description="Retrieve a relationship by source, type, and target",
        parameters=[
            MCPFunctionParameter(
                name="source_id",
                description="Source entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="relationship_type",
                description="Type of relationship",
                required=True
            ),
            MCPFunctionParameter(
                name="target_id",
                description="Target entity identifier",
                required=True
            )
        ]
    )
    async def get_relationship(source_id: str, relationship_type: str, target_id: str) -> Dict[str, Any]:
        """
        Retrieve a relationship by source, type, and target.
        
        Args:
            source_id (str): Source entity identifier
            relationship_type (str): Type of relationship
            target_id (str): Target entity identifier
        
        Returns:
            Dict[str, Any]: Relationship details or error message
        """
        logger.info(f"Retrieving relationship '{relationship_type}' from '{source_id}' to '{target_id}'")
        
        try:
            # Query to find relationship
            query = f"""
            MATCH (source:Entity {{id: $source_id}})-[r:{relationship_type}]->(target:Entity {{id: $target_id}})
            RETURN r
            """
            
            # Execute query
            result = db_connection.execute_query(query, {
                "source_id": source_id,
                "target_id": target_id
            })
            
            if not result:
                return {
                    "success": False,
                    "message": f"Relationship '{relationship_type}' from '{source_id}' to '{target_id}' not found"
                }
            
            # Extract relationship data
            relationship = result[0]["r"]
            
            return {
                "success": True,
                "relationship": relationship,
                "source_id": source_id,
                "relationship_type": relationship_type,
                "target_id": target_id
            }
        except Exception as e:
            logger.error(f"Failed to retrieve relationship: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to retrieve relationship: {str(e)}"
            }

    @server.register_function(
        name="delete_relationship",
        description="Delete a relationship between entities",
        parameters=[
            MCPFunctionParameter(
                name="source_id",
                description="Source entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="relationship_type",
                description="Type of relationship",
                required=True
            ),
            MCPFunctionParameter(
                name="target_id",
                description="Target entity identifier",
                required=True
            )
        ]
    )
    async def delete_relationship(source_id: str, relationship_type: str, target_id: str) -> Dict[str, Any]:
        """
        Delete a relationship between entities.
        
        Args:
            source_id (str): Source entity identifier
            relationship_type (str): Type of relationship
            target_id (str): Target entity identifier
        
        Returns:
            Dict[str, Any]: Deletion result or error message
        """
        logger.info(f"Deleting relationship '{relationship_type}' from '{source_id}' to '{target_id}'")
        
        try:
            # First, check if relationship exists
            query_check = f"""
            MATCH (source:Entity {{id: $source_id}})-[r:{relationship_type}]->(target:Entity {{id: $target_id}})
            RETURN r
            """
            
            result = db_connection.execute_query(query_check, {
                "source_id": source_id,
                "target_id": target_id
            })
            
            if not result:
                return {
                    "success": False,
                    "message": f"Relationship '{relationship_type}' from '{source_id}' to '{target_id}' not found"
                }
            
            # Delete relationship
            query = f"""
            MATCH (source:Entity {{id: $source_id}})-[r:{relationship_type}]->(target:Entity {{id: $target_id}})
            DELETE r
            """
            
            # Execute query
            db_connection.execute_write_query(query, {
                "source_id": source_id,
                "target_id": target_id
            })
            
            return {
                "success": True,
                "source_id": source_id,
                "relationship_type": relationship_type,
                "target_id": target_id,
                "message": "Relationship deleted successfully"
            }
        except Exception as e:
            logger.error(f"Failed to delete relationship: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to delete relationship: {str(e)}"
            }
    
    @server.register_function(
        name="list_relationships",
        description="List relationships with filtering and pagination",
        parameters=[
            MCPFunctionParameter(
                name="entity_id",
                description="Entity identifier to find relationships for",
                required=False
            ),
            MCPFunctionParameter(
                name="relationship_type",
                description="Filter by relationship type",
                required=False
            ),
            MCPFunctionParameter(
                name="direction",
                description="Relationship direction ('outgoing', 'incoming', or 'both')",
                required=False
            ),
            MCPFunctionParameter(
                name="page",
                description="Page number (0-based)",
                required=False
            ),
            MCPFunctionParameter(
                name="page_size",
                description="Number of results per page",
                required=False
            )
        ]
    )
    async def list_relationships(entity_id: Optional[str] = None,
                             relationship_type: Optional[str] = None,
                             direction: Optional[str] = "both",
                             page: Optional[int] = 0,
                             page_size: Optional[int] = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
        """
        List relationships with filtering and pagination.
        
        Args:
            entity_id (Optional[str]): Entity identifier to find relationships for
            relationship_type (Optional[str]): Filter by relationship type
            direction (Optional[str]): Relationship direction ('outgoing', 'incoming', or 'both')
            page (Optional[int]): Page number (0-based)
            page_size (Optional[int]): Number of results per page
        
        Returns:
            Dict[str, Any]: List of relationships matching the filters
        """
        logger.info(f"Listing relationships for entity='{entity_id}', type='{relationship_type}', direction='{direction}'")
        
        try:
            # Validate pagination parameters
            if page < 0:
                page = 0
            if page_size <= 0 or page_size > MAX_PAGE_SIZE:
                page_size = DEFAULT_PAGE_SIZE
            
            # Validate direction parameter
            valid_directions = ["outgoing", "incoming", "both"]
            if direction not in valid_directions:
                direction = "both"
            
            # Calculate skip value for pagination
            skip = page * page_size
            
            # Start building the query based on filters
            query_parts = []
            count_query_parts = []
            params = {}
            
            # Entity filter
            if entity_id:
                params["entity_id"] = entity_id
                
                if direction == "outgoing" or direction == "both":
                    outgoing_match = "MATCH (source:Entity {id: $entity_id})-[r"  # Relationship type will be added conditionally
                    if relationship_type:
                        outgoing_match += f":{relationship_type}"
                    outgoing_match += "]->(target:Entity)"
                    query_parts.append(outgoing_match)
                    count_query_parts.append(outgoing_match)
                
                if direction == "incoming" or direction == "both":
                    incoming_match = "MATCH (source:Entity)-[r"  # Relationship type will be added conditionally
                    if relationship_type:
                        incoming_match += f":{relationship_type}"
                    incoming_match += "]->(target:Entity {id: $entity_id})"
                    
                    if direction == "both" and query_parts:  # If we already added outgoing
                        query_parts.append("UNION")
                        count_query_parts.append("UNION")
                    
                    query_parts.append(incoming_match)
                    count_query_parts.append(incoming_match)
            else:
                # No entity specified, get all relationships
                base_match = "MATCH (source:Entity)-[r"
                if relationship_type:
                    base_match += f":{relationship_type}"
                base_match += "]->(target:Entity)"
                query_parts.append(base_match)
                count_query_parts.append(base_match)
            
            # Add return clause for main query
            query_parts.append("RETURN source.id AS source_id, type(r) AS relationship_type, target.id AS target_id, r AS relationship")
            
            # Add pagination
            query_parts.append(f"SKIP {skip} LIMIT {page_size}")
            
            # Return count only for count query
            count_query_parts.append("RETURN count(*) AS count")
            
            # Build the final queries
            query = " ".join(query_parts)
            count_query = " ".join(count_query_parts)
            
            # Get total count for pagination
            count_result = db_connection.execute_query(count_query, params)
            total_count = count_result[0]["count"] if count_result else 0
            
            # Execute the main query
            result = db_connection.execute_query(query, params)
            
            # Extract relationships from result
            relationships = []
            for record in result:
                rel_entry = {
                    "source_id": record["source_id"],
                    "relationship_type": record["relationship_type"],
                    "target_id": record["target_id"],
                    "properties": record["relationship"]
                }
                relationships.append(rel_entry)
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            has_next = page < total_pages - 1
            has_prev = page > 0
            
            return {
                "success": True,
                "relationships": relationships,
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
            logger.error(f"Failed to list relationships: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to list relationships: {str(e)}"
            }
    
    @server.register_function(
        name="find_path",
        description="Find paths between two entities",
        parameters=[
            MCPFunctionParameter(
                name="source_id",
                description="Source entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="target_id",
                description="Target entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="max_depth",
                description="Maximum path length",
                required=False
            ),
            MCPFunctionParameter(
                name="relationship_types",
                description="Relationship types to consider",
                required=False
            )
        ]
    )
    async def find_path(source_id: str, target_id: str, 
                     max_depth: Optional[int] = 5,
                     relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Find paths between two entities.
        
        Args:
            source_id (str): Source entity identifier
            target_id (str): Target entity identifier
            max_depth (Optional[int]): Maximum path length
            relationship_types (Optional[List[str]]): Relationship types to consider
        
        Returns:
            Dict[str, Any]: Paths between the entities
        """
        logger.info(f"Finding paths from '{source_id}' to '{target_id}'")
        
        try:
            # Validate parameters
            if max_depth <= 0 or max_depth > 10:  # Reasonable limits
                max_depth = 5
            
            # Start building the query
            query_parts = [
                "MATCH path = shortestPath((source:Entity {id: $source_id})-"
            ]
            
            # Add relationship type filter if provided
            rel_filter = "[*..{}]".format(max_depth)
            if relationship_types and len(relationship_types) > 0:
                rel_types = "|".join([f":{t}" for t in relationship_types])
                rel_filter = f"[{rel_types}*..{max_depth}]"
            
            query_parts.append(rel_filter)
            query_parts.append("-(target:Entity {id: $target_id}))")
            
            # Add return clause
            query_parts.append("RETURN path, length(path) AS path_length")
            
            # Build the final query
            query = "".join(query_parts)
            
            # Execute query
            result = db_connection.execute_query(query, {
                "source_id": source_id,
                "target_id": target_id
            })
            
            if not result:
                return {
                    "success": True,
                    "paths": [],
                    "message": "No path found between the entities"
                }
            
            # Extract path information
            paths = []
            for record in result:
                path = record["path"]
                path_length = record["path_length"]
                
                # Extract nodes and relationships from path
                nodes = path.nodes
                relationships = path.relationships
                
                path_info = {
                    "length": path_length,
                    "nodes": [node for node in nodes],
                    "relationships": [rel for rel in relationships]
                }
                
                paths.append(path_info)
            
            return {
                "success": True,
                "paths": paths,
                "source_id": source_id,
                "target_id": target_id,
                "count": len(paths)
            }
        except Exception as e:
            logger.error(f"Failed to find path: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find path: {str(e)}"
            }
    
    logger.info("Relationship API endpoints registered")
