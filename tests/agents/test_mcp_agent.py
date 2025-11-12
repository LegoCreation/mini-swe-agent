"""Tests for MCP-aware agent."""

import json

import pytest

from minisweagent.agents.mcp_agent import MCPAgent, MCPAgentConfig
from minisweagent.environments.local import LocalEnvironment
from minisweagent.integrations.github_mcp import MCPToolConfig
from minisweagent.models.test_models import DeterministicModel


def test_mcp_agent_config_defaults():
    """Test that MCPAgentConfig has sensible defaults."""
    config = MCPAgentConfig()
    assert config.enable_mcp_tools is True
    assert config.mcp_tool_choice == "auto"


def test_mcp_agent_initialization():
    """Test that MCPAgent initializes correctly."""
    model = DeterministicModel(outputs=["echo 'test'"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    assert agent.mcp_client is not None
    assert agent.config.enable_mcp_tools is True


def test_mcp_agent_initialization_with_custom_config():
    """Test MCPAgent initialization with custom MCP config."""
    model = DeterministicModel(outputs=["echo 'test'"])
    env = LocalEnvironment()
    mcp_config = MCPToolConfig(enabled_tools=["search_repositories"])
    
    agent = MCPAgent(model, env, mcp_config=mcp_config)
    
    assert agent.mcp_client.config.enabled_tools == ["search_repositories"]


def test_mcp_agent_parse_bash_action():
    """Test that MCPAgent can parse regular bash actions."""
    model = DeterministicModel(outputs=["```bash\necho 'test'\n```"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    response = {"content": "```bash\necho 'test'\n```"}
    action = agent.parse_action(response)
    
    assert action["action"] == "echo 'test'"
    assert "action_type" not in action


def test_mcp_agent_parse_mcp_action():
    """Test that MCPAgent can parse MCP tool calls."""
    model = DeterministicModel(outputs=["@mcp_call{\"tool\": \"search_repositories\", \"args\": {\"query\": \"test\"}}"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    response = {"content": "@mcp_call{\"tool\": \"search_repositories\", \"args\": {\"query\": \"test\"}}"}
    action = agent.parse_action(response)
    
    assert action["action_type"] == "mcp"
    assert action["tool"] == "search_repositories"
    assert action["args"] == {"query": "test"}


def test_mcp_agent_parse_invalid_mcp_call():
    """Test that invalid MCP calls fall back to bash parsing."""
    model = DeterministicModel(outputs=["@mcp_call{invalid json}"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    response = {"content": "@mcp_call{invalid json}\n```bash\necho 'fallback'\n```"}
    action = agent.parse_action(response)
    
    # Should fall back to bash
    assert action["action"] == "echo 'fallback'"


def test_mcp_agent_execute_bash_action():
    """Test that MCPAgent can execute bash actions."""
    model = DeterministicModel(outputs=["```bash\necho 'test'\n```"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    action = {"action": "echo 'test'"}
    result = agent.execute_action(action)
    
    assert "output" in result
    assert "test" in result["output"]


def test_mcp_agent_execute_mcp_action():
    """Test that MCPAgent can execute MCP actions."""
    model = DeterministicModel(outputs=["@mcp_call{\"tool\": \"list_issues\", \"args\": {}}"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    action = {
        "action_type": "mcp",
        "tool": "list_issues",
        "args": {"owner": "test", "repo": "test"},
    }
    result = agent.execute_action(action)
    
    assert "output" in result
    # The placeholder implementation returns a JSON response
    output_data = json.loads(result["output"])
    assert "status" in output_data or "message" in output_data


def test_mcp_agent_disabled_mcp():
    """Test that MCP can be disabled."""
    model = DeterministicModel(outputs=["```bash\necho 'test'\n```"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env, enable_mcp_tools=False)
    
    assert agent.config.enable_mcp_tools is False
    
    # MCP calls should be ignored when disabled
    response = {"content": "@mcp_call{\"tool\": \"search\", \"args\": {}}\n```bash\necho 'test'\n```"}
    action = agent.parse_action(response)
    
    # Should parse bash action
    assert action["action"] == "echo 'test'"


def test_mcp_agent_template_vars():
    """Test that MCP tools info is added to template vars."""
    model = DeterministicModel(outputs=["echo 'test'"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    assert "mcp_tools_info" in agent.extra_template_vars
    assert len(agent.extra_template_vars["mcp_tools_info"]) > 0
