"""
Tests for the Knowledge Storage MCP server.
"""

import pytest
from knowledge_storage_mcp.server import create_mcp_server

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    # Create MCP server
    server = create_mcp_server()
    
    # Get health check function
    health_check = server._functions.get("health")
    assert health_check is not None
    
    # Call health check function
    result = await health_check({})
    
    # Check result
    assert result["status"] == "healthy"
    assert "version" in result
