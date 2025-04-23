"""
Neo4j Schema Management Module

This module handles the schema management for the knowledge graph,
including entity types, relationship types, and property validation.
It implements the symbol-concept separation principle and supports
tiered knowledge organization.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

# Local imports
from knowledge_storage_mcp.db.connection import Neo4jConnection
from knowledge_storage_mcp.utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Schema versions
SCHEMA_VERSION = "0.1.0"

class SchemaManager:
    """
    Schema manager for the knowledge graph.
    
    This class manages the schema definitions for entity types,
    relationship types, and their properties, ensuring consistency
    and validation across the knowledge graph.
    """
    
    def __init__(self, connection: Neo4jConnection):
        """
        Initialize the schema manager.
        
        Args:
            connection (Neo4jConnection): Neo4j database connection
        """
        self.connection = connection
        self.entity_types = {}
        self.relationship_types = {}
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """
        Load schema definitions from the schema files.
        
        This method loads entity types and relationship types from 
        JSON schema files located in the schemas directory.
        """
        # Get the schema directory path
        schema_dir = Path(__file__).parent.parent.parent / "schemas"
        
        # Load entity types
        entity_types_path = schema_dir / "entity_types.json"
        if entity_types_path.exists():
            with open(entity_types_path, "r") as f:
                self.entity_types = json.load(f)
            logger.info(f"Loaded {len(self.entity_types)} entity types from {entity_types_path}")
        else:
            logger.warning(f"Entity types schema file not found at {entity_types_path}")
            # Create default entity types
            self.entity_types = {
                "Entity": {
                    "description": "Base entity type",
                    "properties": {
                        "id": {"type": "string", "required": True},
                        "name": {"type": "string", "required": True},
                        "description": {"type": "string", "required": False}
                    }
                },
                "Concept": {
                    "description": "Represents a mathematical concept",
                    "inherits": "Entity",
                    "properties": {
                        "domain": {"type": "string", "required": True},
                        "tier": {"type": "string", "enum": ["L1", "L2", "L3"], "required": True}
                    }
                },
                "Symbol": {
                    "description": "Represents a mathematical symbol or notation",
                    "inherits": "Entity",
                    "properties": {
                        "notation": {"type": "string", "required": True},
                        "latex": {"type": "string", "required": False},
                        "context": {"type": "string", "required": True}
                    }
                }
            }
            # Save default entity types
            os.makedirs(schema_dir, exist_ok=True)
            with open(entity_types_path, "w") as f:
                json.dump(self.entity_types, f, indent=2)
            logger.info(f"Created default entity types schema at {entity_types_path}")
        
        # Load relationship types
        relationship_types_path = schema_dir / "relationship_types.json"
        if relationship_types_path.exists():
            with open(relationship_types_path, "r") as f:
                self.relationship_types = json.load(f)
            logger.info(f"Loaded {len(self.relationship_types)} relationship types from {relationship_types_path}")
        else:
            logger.warning(f"Relationship types schema file not found at {relationship_types_path}")
            # Create default relationship types
            self.relationship_types = {
                "REPRESENTS": {
                    "description": "Symbol represents a concept",
                    "source_types": ["Symbol"],
                    "target_types": ["Concept"],
                    "properties": {
                        "context": {"type": "string", "required": False},
                        "confidence": {"type": "number", "min": 0, "max": 1, "required": False}
                    }
                },
                "RELATES_TO": {
                    "description": "Concept relates to another concept",
                    "source_types": ["Concept"],
                    "target_types": ["Concept"],
                    "properties": {
                        "relationship_type": {"type": "string", "required": True},
                        "description": {"type": "string", "required": False}
                    }
                },
                "APPEARS_IN": {
                    "description": "Symbol or concept appears in a document",
                    "source_types": ["Symbol", "Concept"],
                    "target_types": ["Document"],
                    "properties": {
                        "location": {"type": "string", "required": False},
                        "context": {"type": "string", "required": False}
                    }
                }
            }
            # Save default relationship types
            os.makedirs(schema_dir, exist_ok=True)
            with open(relationship_types_path, "w") as f:
                json.dump(self.relationship_types, f, indent=2)
            logger.info(f"Created default relationship types schema at {relationship_types_path}")
    
    def get_entity_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """
        Get entity type definition.
        
        Args:
            type_name (str): Entity type name
        
        Returns:
            Optional[Dict[str, Any]]: Entity type definition or None if not found
        """
        return self.entity_types.get(type_name)
    
    def get_relationship_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """
        Get relationship type definition.
        
        Args:
            type_name (str): Relationship type name
        
        Returns:
            Optional[Dict[str, Any]]: Relationship type definition or None if not found
        """
        return self.relationship_types.get(type_name)
    
    def validate_entity(self, entity_type: str, properties: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate entity properties against the schema.
        
        Args:
            entity_type (str): Entity type name
            properties (Dict[str, Any]): Entity properties
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Check if entity type exists
        type_def = self.get_entity_type(entity_type)
        if not type_def:
            return False, [f"Entity type '{entity_type}' does not exist"]
        
        # Collect all properties to check (including inherited ones)
        all_properties = {}
        current_type = type_def
        
        # Handle inheritance
        while current_type:
            # Add properties from current type
            all_properties.update(current_type.get("properties", {}))
            
            # Check for parent type
            parent_type_name = current_type.get("inherits")
            if parent_type_name:
                current_type = self.get_entity_type(parent_type_name)
                if not current_type:
                    errors.append(f"Parent type '{parent_type_name}' does not exist")
                    break
            else:
                current_type = None
        
        # Check required properties
        for prop_name, prop_def in all_properties.items():
            if prop_def.get("required", False) and prop_name not in properties:
                errors.append(f"Required property '{prop_name}' is missing")
        
        # Check property types and constraints
        for prop_name, prop_value in properties.items():
            prop_def = all_properties.get(prop_name)
            
            # Check if property is defined in schema
            if not prop_def:
                errors.append(f"Property '{prop_name}' is not defined in schema for type '{entity_type}'")
                continue
            
            # Check property type
            prop_type = prop_def.get("type")
            if prop_type == "string" and not isinstance(prop_value, str):
                errors.append(f"Property '{prop_name}' should be a string")
            elif prop_type == "number" and not isinstance(prop_value, (int, float)):
                errors.append(f"Property '{prop_name}' should be a number")
            elif prop_type == "boolean" and not isinstance(prop_value, bool):
                errors.append(f"Property '{prop_name}' should be a boolean")
            elif prop_type == "array" and not isinstance(prop_value, list):
                errors.append(f"Property '{prop_name}' should be an array")
            elif prop_type == "object" and not isinstance(prop_value, dict):
                errors.append(f"Property '{prop_name}' should be an object")
            
            # Check enum constraint
            if "enum" in prop_def and prop_value not in prop_def["enum"]:
                allowed_values = ", ".join([str(v) for v in prop_def["enum"]])
                errors.append(f"Property '{prop_name}' should be one of: {allowed_values}")
            
            # Check min/max constraints for numbers
            if prop_type == "number":
                if "min" in prop_def and prop_value < prop_def["min"]:
                    errors.append(f"Property '{prop_name}' should be at least {prop_def['min']}")
                if "max" in prop_def and prop_value > prop_def["max"]:
                    errors.append(f"Property '{prop_name}' should be at most {prop_def['max']}")
            
            # Check min/max length constraints for strings
            if prop_type == "string":
                if "minLength" in prop_def and len(prop_value) < prop_def["minLength"]:
                    errors.append(f"Property '{prop_name}' should have at least {prop_def['minLength']} characters")
                if "maxLength" in prop_def and len(prop_value) > prop_def["maxLength"]:
                    errors.append(f"Property '{prop_name}' should have at most {prop_def['maxLength']} characters")
        
        return len(errors) == 0, errors
    
    def validate_relationship(self, relationship_type: str, source_type: str, target_type: str, 
                              properties: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate relationship properties and types against the schema.
        
        Args:
            relationship_type (str): Relationship type name
            source_type (str): Source entity type
            target_type (str): Target entity type
            properties (Dict[str, Any]): Relationship properties
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Check if relationship type exists
        type_def = self.get_relationship_type(relationship_type)
        if not type_def:
            return False, [f"Relationship type '{relationship_type}' does not exist"]
        
        # Check source type
        if "source_types" in type_def:
            allowed_source_types = type_def["source_types"]
            if source_type not in allowed_source_types:
                allowed_types_str = ", ".join(allowed_source_types)
                errors.append(f"Source type '{source_type}' is not allowed for relationship '{relationship_type}'. Allowed types: {allowed_types_str}")
        
        # Check target type
        if "target_types" in type_def:
            allowed_target_types = type_def["target_types"]
            if target_type not in allowed_target_types:
                allowed_types_str = ", ".join(allowed_target_types)
                errors.append(f"Target type '{target_type}' is not allowed for relationship '{relationship_type}'. Allowed types: {allowed_types_str}")
        
        # Check required properties
        relationship_properties = type_def.get("properties", {})
        for prop_name, prop_def in relationship_properties.items():
            if prop_def.get("required", False) and prop_name not in properties:
                errors.append(f"Required property '{prop_name}' is missing")
        
        # Check property types and constraints
        for prop_name, prop_value in properties.items():
            prop_def = relationship_properties.get(prop_name)
            
            # Check if property is defined in schema
            if not prop_def:
                errors.append(f"Property '{prop_name}' is not defined in schema for relationship type '{relationship_type}'")
                continue
            
            # Check property type
            prop_type = prop_def.get("type")
            if prop_type == "string" and not isinstance(prop_value, str):
                errors.append(f"Property '{prop_name}' should be a string")
            elif prop_type == "number" and not isinstance(prop_value, (int, float)):
                errors.append(f"Property '{prop_name}' should be a number")
            elif prop_type == "boolean" and not isinstance(prop_value, bool):
                errors.append(f"Property '{prop_name}' should be a boolean")
            elif prop_type == "array" and not isinstance(prop_value, list):
                errors.append(f"Property '{prop_name}' should be an array")
            elif prop_type == "object" and not isinstance(prop_value, dict):
                errors.append(f"Property '{prop_name}' should be an object")
            
            # Check enum constraint
            if "enum" in prop_def and prop_value not in prop_def["enum"]:
                allowed_values = ", ".join([str(v) for v in prop_def["enum"]])
                errors.append(f"Property '{prop_name}' should be one of: {allowed_values}")
            
            # Check min/max constraints for numbers
            if prop_type == "number":
                if "min" in prop_def and prop_value < prop_def["min"]:
                    errors.append(f"Property '{prop_name}' should be at least {prop_def['min']}")
                if "max" in prop_def and prop_value > prop_def["max"]:
                    errors.append(f"Property '{prop_name}' should be at most {prop_def['max']}")
            
            # Check min/max length constraints for strings
            if prop_type == "string":
                if "minLength" in prop_def and len(prop_value) < prop_def["minLength"]:
                    errors.append(f"Property '{prop_name}' should have at least {prop_def['minLength']} characters")
                if "maxLength" in prop_def and len(prop_value) > prop_def["maxLength"]:
                    errors.append(f"Property '{prop_name}' should have at most {prop_def['maxLength']} characters")
        
        return len(errors) == 0, errors
    
    def get_all_entity_types(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all entity type definitions.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of entity type definitions
        """
        return self.entity_types
    
    def get_all_relationship_types(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all relationship type definitions.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of relationship type definitions
        """
        return self.relationship_types
