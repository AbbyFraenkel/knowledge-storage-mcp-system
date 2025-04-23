# Knowledge Storage MCP

[![Test](https://github.com/AbbyFraenkel/knowledge-storage-mcp-system/actions/workflows/test.yml/badge.svg)](https://github.com/AbbyFraenkel/knowledge-storage-mcp-system/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Model Context Protocol (MCP) server provides a robust, scalable infrastructure for storing, retrieving, and querying knowledge entities, relationships, and their associated metadata extracted from scientific papers.

## Core Functionality

- Entity and relationship storage with comprehensive metadata
- Schema validation and enforcement for academic content
- Efficient query capabilities with specialized patterns for academic knowledge
- Versioning and provenance tracking
- Cross-referencing between knowledge entities

## Architectural Principles

The Knowledge Storage MCP implements these core principles:

### 1. Symbol-Concept Separation

Symbols (notation) are stored separately from concepts (meaning) with explicit REPRESENTS relationships between them. This allows:

- The same concept to have multiple notational representations
- The same symbol to represent different concepts in different contexts
- Clear disambiguation of mathematical notation

### 2. Tiered Knowledge Organization

Knowledge is organized in three tiers for efficient context window usage:

- **L1**: Core concepts (100-200 words)
- **L2**: Functional details (500-1000 words)
- **L3**: Complete knowledge (2000+ words)

This tiered approach enables efficient knowledge retrieval at appropriate detail levels.

### 3. Cross-Domain Mapping

The MCP supports explicit mappings between concepts across different domains through specialized relationship types such as HAS_INTERPRETATION_IN. This enables:

- Translation between pure mathematical concepts and domain applications
- Context-aware interpretation of concepts
- Knowledge transfer across disciplinary boundaries

## Components

### API Layer

The MCP exposes these primary API endpoints:

#### Entity Management
- `create_entity`: Create entities with validation
- `get_entity`: Retrieve entity details
- `update_entity`: Update entity properties
- `delete_entity`: Remove entities with relationship handling
- `list_entities`: Query entities with filtering and pagination
- `get_entity_by_properties`: Find entities by property values

#### Relationship Management
- `create_relationship`: Create validated relationships between entities
- `get_relationship`: Retrieve relationship details
- `delete_relationship`: Remove relationships
- `list_relationships`: Query relationships with filtering
- `find_path`: Find paths between entities

#### Specialized Academic Queries
- `find_symbols_for_concept`: Supporting symbol-concept separation
- `find_concepts_for_symbol`: Resolving symbol ambiguity
- `get_entity_with_tier`: Tiered knowledge organization (L1, L2, L3)
- `find_cross_domain_mappings`: Cross-domain knowledge linking

### Schema Management

The MCP implements robust schema management with:

- Entity type definitions with inheritance support
- Relationship type validation
- Property validation for both entities and relationships
- Schema evolution capabilities

### Neo4j Integration

The knowledge is stored in a Neo4j graph database with:

- Optimized Cypher queries for academic knowledge
- Efficient indexing for common query patterns
- Transaction management for data integrity
- Backup and recovery mechanisms

## Integration

This MCP integrates with:

- **Document Processing MCP**: Receives structured document content
- **Equation Processing MCP**: Stores processed equations with symbol-concept mappings
- **Text Extraction MCP**: Captures entity relationships from text
- **Knowledge Integration MCP**: Facilitates knowledge synthesis
- **Knowledge Explorer MCP**: Enables knowledge exploration

## Setup and Usage

### Prerequisites
- Python 3.10+
- Neo4j database (5.x recommended)
- Model Context Protocol SDK

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
MCP_PORT=8000
LOG_LEVEL=INFO
```

### Running the Server

```bash
# Start the server
python -m knowledge_storage_mcp.server
```

### Docker Deployment

```bash
# Build and start with Docker Compose
docker-compose up -d
```

### Using with Claude

This MCP can be used with Claude through the Model Context Protocol to provide knowledge storage and retrieval capabilities.

Example usage:

```python
from modelcontextprotocol import MCPClient

# Connect to Knowledge Storage MCP
client = MCPClient("http://localhost:8000")

# Create a mathematical concept
response = client.invoke_function(
    "create_entity",
    {
        "entity_type": "Concept",
        "properties": {
            "name": "Finite Element Method",
            "description": "Numerical technique for solving PDEs",
            "domain": "numerical_methods",
            "tier": "L1"
        }
    }
)

concept_id = response["entity_id"]

# Create a symbol for the concept
response = client.invoke_function(
    "create_entity",
    {
        "entity_type": "Symbol",
        "properties": {
            "name": "FEM Notation",
            "notation": "FEM",
            "latex": "\\text{FEM}",
            "context": "Numerical methods literature"
        }
    }
)

symbol_id = response["entity_id"]

# Create relationship between symbol and concept
response = client.invoke_function(
    "create_relationship",
    {
        "from_entity_id": symbol_id,
        "relationship_type": "REPRESENTS",
        "to_entity_id": concept_id,
        "properties": {
            "context": "Numerical methods literature",
            "confidence": 1.0
        }
    }
)
```

## Development

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=knowledge_storage_mcp
```

### Linting and Type Checking

```bash
# Lint
flake8 knowledge_storage_mcp tests

# Type check
mypy knowledge_storage_mcp
```

## Project Structure

```
knowledge-storage-mcp/
├── .github/
│   └── workflows/        # GitHub Actions workflows
├── docker/               # Docker configuration
├── knowledge_storage_mcp/
│   ├── api/              # API endpoints
│   │   ├── entities.py   # Entity management
│   │   ├── relationships.py # Relationship management
│   │   └── queries.py    # Specialized queries
│   ├── db/               # Database integration
│   │   ├── connection.py # Neo4j connection
│   │   └── schema.py     # Schema management
│   ├── models/           # Data models
│   ├── utils/            # Utility functions
│   └── server.py         # MCP server implementation
├── schemas/              # Schema definitions
│   ├── entity_types.json # Entity type definitions
│   └── relationship_types.json # Relationship type definitions
├── tests/                # Test suite
├── docker-compose.yml    # Docker Compose configuration
├── pyproject.toml        # Project metadata
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.