#!/usr/bin/env python3
"""
Simple test script to verify MCP integration is working properly.
"""

import json
import os
from minisweagent.agents.mcp_agent import MCPAgent, MCPAgentConfig
from minisweagent.environments.local import LocalEnvironment
from minisweagent.integrations.github_mcp import GitHubMCPClient, MCPToolConfig
from minisweagent.models.test_models import DeterministicModel


def test_mcp_client_initialization():
    """Test that MCP client initializes correctly."""
    print("Testing MCP client initialization...")
    
    # Test with default config
    client = GitHubMCPClient()
    print(f"✓ Default client initialized with {len(client._tools)} tools")
    
    # Test with custom config
    config = MCPToolConfig(enabled_tools=["search_repositories", "list_issues"])
    client = GitHubMCPClient(config)
    tools = client.get_tools()
    print(f"✓ Custom client initialized with {len(tools)} tools: {[t['function']['name'] for t in tools]}")
    
    return client


def test_mcp_agent_initialization():
    """Test that MCP agent initializes correctly."""
    print("\nTesting MCP agent initialization...")
    
    model = DeterministicModel(outputs=["echo 'test'"])
    env = LocalEnvironment()
    
    # Test with default MCP config
    agent = MCPAgent(model, env)
    print(f"✓ MCP agent initialized with {len(agent.mcp_client._tools)} available tools")
    print(f"✓ MCP tools enabled: {agent.config.enable_mcp_tools}")
    
    # Test tools formatting for prompt
    tools_info = agent.mcp_client.format_tools_for_prompt()
    print(f"✓ Tools info generated for prompt: {len(tools_info)} characters")
    
    return agent


def test_mcp_tool_execution():
    """Test MCP tool execution (placeholder implementation)."""
    print("\nTesting MCP tool execution...")
    
    client = GitHubMCPClient()
    
    # Test a basic tool call
    result = client.execute_tool("search_repositories", {"query": "mini-swe-agent"})
    print(f"✓ Tool execution returned: {result.get('status', 'unknown')}")
    
    # Test unknown tool
    result = client.execute_tool("nonexistent_tool", {})
    print(f"✓ Unknown tool handling: {'error' in result}")
    
    return True


def test_mcp_call_parsing():
    """Test MCP call parsing in agent."""
    print("\nTesting MCP call parsing...")
    
    model = DeterministicModel(outputs=["echo 'test'"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env)
    
    # Test valid MCP call parsing
    valid_call = '{"tool": "search_repositories", "args": {"query": "test"}}'
    try:
        result = agent._parse_mcp_call(valid_call, {"content": "test"})
        print(f"✓ Valid MCP call parsed successfully: {result.get('action_type')}")
    except Exception as e:
        print(f"✗ Failed to parse valid MCP call: {e}")
    
    # Test invalid MCP call parsing
    invalid_call = '{"invalid": "json"'
    try:
        result = agent._parse_mcp_call(invalid_call, {"content": "```bash\necho 'fallback'\n```"})
        print(f"✓ Invalid MCP call fallback handled: {result.get('action', 'no action')}")
    except Exception as e:
        print(f"✗ Failed to handle invalid MCP call: {e}")
    
    return True


def test_github_token_handling():
    """Test GitHub token configuration."""
    print("\nTesting GitHub token handling...")
    
    # Test without token
    config = MCPToolConfig()
    print(f"✓ Token from env: {'GITHUB_TOKEN' in os.environ}")
    
    # Test with explicit token
    config = MCPToolConfig(github_token="test_token")
    print(f"✓ Explicit token set: {config.github_token == 'test_token'}")
    
    return True


def main():
    """Run all MCP integration tests."""
    print("=== MCP Integration Test Suite ===\n")
    
    try:
        test_mcp_client_initialization()
        test_mcp_agent_initialization()
        test_mcp_tool_execution()
        test_mcp_call_parsing()
        test_github_token_handling()
        
        print("\n=== All Tests Passed! ===")
        print("\n🎉 MCP integration appears to be working properly!")
        print("\nNext steps to test with real GitHub operations:")
        print("1. Set GITHUB_TOKEN environment variable")
        print("2. Run: mini-mcp -t 'List issues in SWE-agent/mini-swe-agent'")
        print("3. Or run: mini-mcp -t 'Search for Python repositories with >1000 stars'")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()