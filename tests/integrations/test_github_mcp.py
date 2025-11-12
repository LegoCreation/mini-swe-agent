"""Tests for GitHub MCP integration."""

import pytest

from minisweagent.integrations.github_mcp import GitHubMCPClient, MCPToolConfig


def test_mcp_tool_config_defaults():
    """Test that MCPToolConfig has sensible defaults."""
    config = MCPToolConfig()
    assert config.enabled_tools is not None
    assert len(config.enabled_tools) > 0
    assert "search_repositories" in config.enabled_tools
    assert "create_issue" in config.enabled_tools


def test_mcp_tool_config_custom_tools():
    """Test that MCPToolConfig can be customized."""
    config = MCPToolConfig(enabled_tools=["search_repositories", "list_issues"])
    assert len(config.enabled_tools) == 2
    assert "search_repositories" in config.enabled_tools
    assert "list_issues" in config.enabled_tools


def test_github_mcp_client_initialization():
    """Test that GitHubMCPClient initializes correctly."""
    client = GitHubMCPClient()
    assert client.config is not None
    assert client._tools is not None
    assert len(client._tools) > 0


def test_github_mcp_client_get_tools():
    """Test that get_tools returns properly formatted tools."""
    client = GitHubMCPClient()
    tools = client.get_tools()
    
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    for tool in tools:
        assert "type" in tool
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]


def test_github_mcp_client_get_specific_tools():
    """Test that client respects enabled_tools config."""
    config = MCPToolConfig(enabled_tools=["search_repositories", "list_issues"])
    client = GitHubMCPClient(config)
    tools = client.get_tools()
    
    tool_names = [tool["function"]["name"] for tool in tools]
    assert "search_repositories" in tool_names
    assert "list_issues" in tool_names
    assert len(tool_names) == 2


def test_github_mcp_client_execute_tool():
    """Test that execute_tool returns expected format."""
    client = GitHubMCPClient()
    result = client.execute_tool("search_repositories", {"query": "test"})
    
    assert isinstance(result, dict)
    assert "status" in result or "message" in result


def test_github_mcp_client_execute_unknown_tool():
    """Test that execute_tool handles unknown tools gracefully."""
    client = GitHubMCPClient()
    result = client.execute_tool("nonexistent_tool", {})
    
    assert isinstance(result, dict)
    assert "error" in result


def test_github_mcp_client_format_tools_for_prompt():
    """Test that format_tools_for_prompt returns a string."""
    client = GitHubMCPClient()
    prompt_text = client.format_tools_for_prompt()
    
    assert isinstance(prompt_text, str)
    assert len(prompt_text) > 0
    assert "GitHub MCP Tools" in prompt_text


def test_github_mcp_client_format_tools_empty():
    """Test format_tools_for_prompt with no enabled tools."""
    config = MCPToolConfig(enabled_tools=[])
    client = GitHubMCPClient(config)
    prompt_text = client.format_tools_for_prompt()
    
    assert prompt_text == ""


@pytest.mark.parametrize(
    ("tool_name", "expected_params"),
    [
        ("search_repositories", ["query"]),
        ("get_file_contents", ["owner", "repo", "path"]),
        ("create_issue", ["owner", "repo", "title"]),
        ("create_pull_request", ["owner", "repo", "title", "head", "base"]),
    ],
)
def test_tool_parameters(tool_name, expected_params):
    """Test that tools have expected parameters."""
    client = GitHubMCPClient()
    tools = client.get_tools()
    
    tool = next((t for t in tools if t["function"]["name"] == tool_name), None)
    assert tool is not None, f"Tool {tool_name} not found"
    
    params = tool["function"]["parameters"]
    assert "required" in params
    
    for param in expected_params:
        assert param in params["required"]
