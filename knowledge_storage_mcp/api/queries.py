    @server.register_function(
        name="find_concepts_for_symbol",
        description="Find all concepts represented by a symbol",
        parameters=[
            MCPFunctionParameter(
                name="symbol_id",
                description="Symbol identifier",
                required=True
            )
        ]
    )
    async def find_concepts_for_symbol(symbol_id: str) -> Dict[str, Any]:
        """
        Find all concepts represented by a symbol.
        This is useful for resolving symbol ambiguity.
        
        Args:
            symbol_id (str): Symbol identifier
        
        Returns:
            Dict[str, Any]: Concepts represented by the symbol
        """
        logger.info(f"Finding concepts for symbol '{symbol_id}'")
        
        try:
            # First, verify that the symbol exists
            query_symbol = """
            MATCH (s:Symbol {id: $symbol_id})
            RETURN s
            """
            
            symbol_result = db_connection.execute_query(query_symbol, {"symbol_id": symbol_id})
            
            if not symbol_result:
                return {
                    "success": False,
                    "message": f"Symbol with ID '{symbol_id}' not found"
                }
            
            # Find all concepts that this symbol REPRESENTS
            query = """
            MATCH (s:Symbol {id: $symbol_id})-[r:REPRESENTS]->(c:Concept)
            RETURN c AS concept, r AS relationship
            """
            
            result = db_connection.execute_query(query, {"symbol_id": symbol_id})
            
            # Extract symbol data
            symbol = symbol_result[0]["s"]
            
            # Process results
            concepts = []
            for record in result:
                concept = record["concept"]
                relationship = record["relationship"]
                
                concept_entry = {
                    "concept": concept,
                    "relationship": relationship
                }
                
                concepts.append(concept_entry)
            
            return {
                "success": True,
                "symbol": symbol,
                "concepts": concepts,
                "count": len(concepts)
            }
        except Exception as e:
            logger.error(f"Failed to find concepts for symbol: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find concepts for symbol: {str(e)}"
            }"""
Query API endpoints for the Knowledge Storage MCP.

This module provides endpoints for querying and exploring the knowledge graph.
"""

import logging
from typing import Dict, Any, List, Optional

# MCP SDK imports
from modelcontextprotocol import MCPServer, MCPFunction, MCPFunctionParameter

# Local imports
from knowledge_storage_mcp.db.connection import Neo4jConnection
from knowledge_storage_mcp.utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Default page size for list operations
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

def register_query_endpoints(server: MCPServer, db_connection: Neo4jConnection) -> None:
    """
    Register query API endpoints with the MCP server.
    
    Args:
        server (MCPServer): The MCP server instance
        db_connection (Neo4jConnection): Database connection instance
    """
    logger.info("Registering query API endpoints")
    
    @server.register_function(
        name="search_entities",
        description="Search for entities in the knowledge graph",
        parameters=[
            MCPFunctionParameter(
                name="query",
                description="Search query string",
                required=True
            ),
            MCPFunctionParameter(
                name="entity_types",
                description="Entity types to search",
                required=False
            ),
            MCPFunctionParameter(
                name="limit",
                description="Maximum number of results",
                required=False
            )
        ]
    )
    async def search_entities(query: str, entity_types: Optional[List[str]] = None,
                           limit: Optional[int] = 100) -> Dict[str, Any]:
        """
        Search for entities in the knowledge graph.
        
        Args:
            query (str): Search query string
            entity_types (Optional[List[str]]): Entity types to search
            limit (Optional[int]): Maximum number of results
        
        Returns:
            Dict[str, Any]: Search results
        """
        logger.info(f"Searching for entities with query '{query}'")
        
        try:
            # Set default entity types if not provided
            entity_types = entity_types or ["Concept", "Symbol"]
            
            # Validate limit
            if limit <= 0 or limit > MAX_PAGE_SIZE:
                limit = DEFAULT_PAGE_SIZE
            
            # Prepare Cypher query with entity types filter and fuzzy search
            type_filter = ":".join(["Entity"] + entity_types)  # Add 'Entity' as base label
            
            # Split query into terms for more flexible matching
            terms = query.strip().split()
            where_clauses = []
            
            # Build WHERE clause with multiple property matches 
            for i, term in enumerate(terms):
                term_param = f"term{i}"
                # Search in name, description, and other common properties
                term_clauses = [
                    f"toLower(e.name) CONTAINS toLower(${term_param})",
                    f"toLower(e.description) CONTAINS toLower(${term_param})",
                    # Add more properties to search based on entity types
                    f"toLower(toString(e.notation)) CONTAINS toLower(${term_param})",
                    f"toLower(toString(e.domain)) CONTAINS toLower(${term_param})"
                ]
                where_clauses.append("(" + " OR ".join(term_clauses) + ")")
            
            # Build the full Cypher query
            query_parts = [
                f"MATCH (e:{type_filter})"
            ]
            
            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))
            
            query_parts.append(f"RETURN e LIMIT {limit}")
            
            cypher_query = "\n".join(query_parts)
            
            # Prepare query parameters
            params = {}
            for i, term in enumerate(terms):
                params[f"term{i}"] = term
            
            # Execute query
            result = db_connection.execute_query(cypher_query, params)
            
            # Process results
            entities = []
            for record in result:
                entity = record["e"]
                entities.append(entity)
            
            return {
                "success": True,
                "query": query,
                "entity_types": entity_types,
                "results": entities,
                "count": len(entities),
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Failed to search entities: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to search entities: {str(e)}"
            }
    
    @server.register_function(
        name="find_paths",
        description="Find paths between entities in the knowledge graph",
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
                description="Maximum path depth",
                required=False
            ),
            MCPFunctionParameter(
                name="relationship_types",
                description="Relationship types to consider",
                required=False
            )
        ]
    )
    async def find_paths(source_id: str, target_id: str,
                     max_depth: Optional[int] = 3,
                     relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Find paths between entities in the knowledge graph.
        
        Args:
            source_id (str): Source entity identifier
            target_id (str): Target entity identifier
            max_depth (Optional[int]): Maximum path depth
            relationship_types (Optional[List[str]]): Relationship types to consider
        
        Returns:
            Dict[str, Any]: Path finding results
        """
        logger.info(f"Finding paths from '{source_id}' to '{target_id}' with max depth {max_depth}")
        
        try:
            # Validate parameters
            if max_depth <= 0 or max_depth > 10:  # Reasonable limits
                max_depth = 3
            
            # Start building the query
            query_parts = [
                "MATCH path = allShortestPaths((source:Entity {id: $source_id})-"
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
                nodes = []
                for node in path.nodes:
                    # Extract node data
                    node_data = dict(node)
                    nodes.append(node_data)
                
                relationships = []
                for rel in path.relationships:
                    # Extract relationship data
                    rel_data = {
                        "type": rel.type,
                        "properties": dict(rel)
                    }
                    relationships.append(rel_data)
                
                path_info = {
                    "length": path_length,
                    "nodes": nodes,
                    "relationships": relationships
                }
                
                paths.append(path_info)
            
            return {
                "success": True,
                "source_id": source_id,
                "target_id": target_id,
                "max_depth": max_depth,
                "paths": paths,
                "count": len(paths)
            }
        except Exception as e:
            logger.error(f"Failed to find paths: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find paths: {str(e)}"
            }
    
    # Add more query endpoints here
    
    @server.register_function(
        name="find_symbols_for_concept",
        description="Find all symbols that represent a concept",
        parameters=[
            MCPFunctionParameter(
                name="concept_id",
                description="Concept identifier",
                required=True
            )
        ]
    )
    async def find_symbols_for_concept(concept_id: str) -> Dict[str, Any]:
        """
        Find all symbols that represent a concept.
        This is a key function for the symbol-concept separation principle.
        
        Args:
            concept_id (str): Concept identifier
        
        Returns:
            Dict[str, Any]: Symbols representing the concept
        """
        logger.info(f"Finding symbols for concept '{concept_id}'")
        
        try:
            # First, verify that the concept exists
            query_concept = """
            MATCH (c:Concept {id: $concept_id})
            RETURN c
            """
            
            concept_result = db_connection.execute_query(query_concept, {"concept_id": concept_id})
            
            if not concept_result:
                return {
                    "success": False,
                    "message": f"Concept with ID '{concept_id}' not found"
                }
            
            # Find all symbols that REPRESENTS this concept
            query = """
            MATCH (s:Symbol)-[r:REPRESENTS]->(c:Concept {id: $concept_id})
            RETURN s AS symbol, r AS relationship
            """
            
            result = db_connection.execute_query(query, {"concept_id": concept_id})
            
            # Extract concept data
            concept = concept_result[0]["c"]
            
            # Process results
            symbols = []
            for record in result:
                symbol = record["symbol"]
                relationship = record["relationship"]
                
                symbol_entry = {
                    "symbol": symbol,
                    "relationship": relationship
                }
                
                symbols.append(symbol_entry)
            
            return {
                "success": True,
                "concept": concept,
                "symbols": symbols,
                "count": len(symbols)
            }
        except Exception as e:
            logger.error(f"Failed to find symbols for concept: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find symbols for concept: {str(e)}"
            }
    
    @server.register_function(
        name="find_concepts_for_symbol",
        description="Find all concepts represented by a symbol",
        parameters=[
            MCPFunctionParameter(
                name="symbol_id",
                description="Symbol identifier",
                required=True
            )
        ]
    )
    async def find_concepts_for_symbol(symbol_id: str) -> Dict[str, Any]:
        """
        Find all concepts represented by a symbol.
        This is useful for resolving symbol ambiguity.
        
        Args:
            symbol_id (str): Symbol identifier
        
        Returns:
            Dict[str, Any]: Concepts represented by the symbol
        """
        logger.info(f"Finding concepts for symbol '{symbol_id}'")
        
        try:
            # First, verify that the symbol exists
            query_symbol = """
            MATCH (s:Symbol {id: $symbol_id})
            RETURN s
            """
            
            symbol_result = db_connection.execute_query(query_symbol, {"symbol_id": symbol_id})
            
            if not symbol_result:
                return {
                    "success": False,
                    "message": f"Symbol with ID '{symbol_id}' not found"
                }
            
            # Find all concepts that this symbol REPRESENTS
            query = """
            MATCH (s:Symbol {id: $symbol_id})-[r:REPRESENTS]->(c:Concept)
            RETURN c AS concept, r AS relationship
            """
            
            result = db_connection.execute_query(query, {"symbol_id": symbol_id})
            
            # Extract symbol data
            symbol = symbol_result[0]["s"]
            
            # Process results
            concepts = []
            for record in result:
                concept = record["concept"]
                relationship = record["relationship"]
                
                concept_entry = {
                    "concept": concept,
                    "relationship": relationship
                }
                
                concepts.append(concept_entry)
            
            return {
                "success": True,
                "symbol": symbol,
                "concepts": concepts,
                "count": len(concepts)
            }
        except Exception as e:
            logger.error(f"Failed to find concepts for symbol: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find concepts for symbol: {str(e)}"
            }

    @server.register_function(
        name="get_entity_with_tier",
        description="Get entity information with specific knowledge tier (L1, L2, L3)",
        parameters=[
            MCPFunctionParameter(
                name="entity_id",
                description="Entity identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="tier",
                description="Knowledge tier (L1, L2, L3)",
                required=False
            )
        ]
    )
    async def get_entity_with_tier(entity_id: str, tier: Optional[str] = "L1") -> Dict[str, Any]:
        """
        Get entity information with specific knowledge tier (L1, L2, L3).
        This implements the tiered knowledge organization principle.
        
        Args:
            entity_id (str): Entity identifier
            tier (Optional[str]): Knowledge tier (L1, L2, L3)
        
        Returns:
            Dict[str, Any]: Entity information at the specified tier
        """
        logger.info(f"Getting entity '{entity_id}' with tier '{tier}'")
        
        try:
            # Validate tier parameter
            valid_tiers = ["L1", "L2", "L3"]
            if tier not in valid_tiers:
                tier = "L1"  # Default to L1 if invalid tier
            
            # Query to find entity by ID
            query = """
            MATCH (e:Entity {id: $id})
            RETURN e
            """
            
            # Execute query
            result = db_connection.execute_query(query, {"id": entity_id})
            
            if not result:
                return {
                    "success": False,
                    "message": f"Entity with ID '{entity_id}' not found"
                }
            
            # Extract entity data
            entity = result[0]["e"]
            
            # Check if entity has tier-specific properties
            tier_properties = {}
            for prop, value in entity.items():
                # Check if property is tier-specific
                if prop.endswith(f"_{tier.lower()}"):
                    # Extract base property name without tier suffix
                    base_prop = prop[:-len(f"_{tier.lower()}")]
                    tier_properties[base_prop] = value
                elif not any(prop.endswith(f"_{t.lower()}") for t in valid_tiers):
                    # Include non-tier-specific properties
                    tier_properties[prop] = value
            
            # Extract entity type (labels)
            entity_type = None
            query_labels = """
            MATCH (e:Entity {id: $id})
            RETURN labels(e) AS labels
            """
            labels_result = db_connection.execute_query(query_labels, {"id": entity_id})
            if labels_result and "labels" in labels_result[0]:
                labels = labels_result[0]["labels"]
                # Filter out 'Entity' to get the specific type
                entity_types = [label for label in labels if label != "Entity"]
                if entity_types:
                    entity_type = entity_types[0]
            
            return {
                "success": True,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "tier": tier,
                "properties": tier_properties
            }
        except Exception as e:
            logger.error(f"Failed to get entity with tier: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get entity with tier: {str(e)}"
            }
    @server.register_function(
        name="find_cross_domain_mappings",
        description="Find mappings between domains for a concept",
        parameters=[
            MCPFunctionParameter(
                name="concept_id",
                description="Concept identifier",
                required=True
            ),
            MCPFunctionParameter(
                name="source_domain",
                description="Source domain",
                required=False
            ),
            MCPFunctionParameter(
                name="target_domain",
                description="Target domain",
                required=False
            )
        ]
    )
    async def find_cross_domain_mappings(concept_id: str, 
                                     source_domain: Optional[str] = None,
                                     target_domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Find mappings between domains for a concept.
        This implements the cross-domain mapping principle.
        
        Args:
            concept_id (str): Concept identifier
            source_domain (Optional[str]): Source domain
            target_domain (Optional[str]): Target domain
        
        Returns:
            Dict[str, Any]: Cross-domain mappings for the concept
        """
        logger.info(f"Finding cross-domain mappings for concept '{concept_id}'")
        
        try:
            # First, verify that the concept exists
            query_concept = """
            MATCH (c:Concept {id: $concept_id})
            RETURN c
            """
            
            concept_result = db_connection.execute_query(query_concept, {"concept_id": concept_id})
            
            if not concept_result:
                return {
                    "success": False,
                    "message": f"Concept with ID '{concept_id}' not found"
                }
            
            # Base query parts
            query_parts = [
                "MATCH (c:Concept {id: $concept_id})"
            ]
            
            # Prepare parameters
            params = {"concept_id": concept_id}
            
            # Add domain filters if provided
            domain_filters = []
            if source_domain:
                domain_filters.append("source.domain = $source_domain")
                params["source_domain"] = source_domain
            
            if target_domain:
                domain_filters.append("target.domain = $target_domain")
                params["target_domain"] = target_domain
            
            # Complete the query based on provided domains
            if source_domain or target_domain:
                # Looking for specific cross-domain mapping
                query_parts.append("MATCH (source:Concept)-[r1]->(c),")
                query_parts.append("      (c)-[r2]->(target:Concept)")
                
                # Add WHERE clause for domain filters
                if domain_filters:
                    query_parts.append("WHERE " + " AND ".join(domain_filters))
                
                query_parts.append("RETURN source, r1, target, r2")
            else:
                # Get all domain representations of this concept
                query_parts.append("MATCH (other:Concept)-[r:MAPPED_TO|EQUIVALENT_TO|DERIVED_FROM|APPLIES_TO]-(c)")
                query_parts.append("RETURN other, r")
            
            # Build the final query
            query = "\n".join(query_parts)
            
            # Execute query
            result = db_connection.execute_query(query, params)
            
            # Extract concept data
            concept = concept_result[0]["c"]
            
            # Process results based on query type
            if source_domain or target_domain:
                # Process specific cross-domain mappings
                mappings = []
                for record in result:
                    mapping = {
                        "source": record["source"],
                        "source_relation": record["r1"],
                        "target": record["target"],
                        "target_relation": record["r2"]
                    }
                    mappings.append(mapping)
                
                return {
                    "success": True,
                    "concept": concept,
                    "source_domain": source_domain,
                    "target_domain": target_domain,
                    "mappings": mappings,
                    "count": len(mappings)
                }
            else:
                # Process all domain representations
                domain_concepts = []
                for record in result:
                    other_concept = record["other"]
                    relationship = record["r"]
                    
                    domain_concept = {
                        "concept": other_concept,
                        "relationship": relationship
                    }
                    
                    domain_concepts.append(domain_concept)
                
                return {
                    "success": True,
                    "concept": concept,
                    "domain_concepts": domain_concepts,
                    "count": len(domain_concepts)
                }
        except Exception as e:
            logger.error(f"Failed to find cross-domain mappings: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to find cross-domain mappings: {str(e)}"
            }
            
    logger.info("Query API endpoints registered")
