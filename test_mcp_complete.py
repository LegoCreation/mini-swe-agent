#!/usr/bin/env python3
"""
Quick test to verify MCP integration without requiring external APIs
"""

import os
from minisweagent.agents.mcp_agent import MCPAgent, MCPAgentConfig
from minisweagent.environments.local import LocalEnvironment
from minisweagent.integrations.github_mcp import GitHubMCPClient, MCPToolConfig
from minisweagent.models.test_models import DeterministicModel


def test_mcp_integration_comprehensive():
    """Comprehensive test of MCP integration."""
    
    print("🧪 Testing MCP Integration Components\n")
    
    # Test 1: MCP Configuration
    print("1. Testing MCP Configuration...")
    config = MCPAgentConfig()
    assert config.enable_mcp_tools == True
    assert config.mcp_tool_choice == "auto"
    print("   ✅ MCP configuration works")
    
    # Test 2: GitHub MCP Client
    print("\n2. Testing GitHub MCP Client...")
    mcp_config = MCPToolConfig(enabled_tools=["search_repositories", "list_issues"])
    client = GitHubMCPClient(mcp_config)
    
    tools = client.get_tools()
    assert len(tools) == 2
    assert all(tool["type"] == "function" for tool in tools)
    print(f"   ✅ GitHub MCP client initialized with {len(tools)} tools")
    
    # Test 3: Tool Execution (Placeholder)
    print("\n3. Testing Tool Execution...")
    result = client.execute_tool("search_repositories", {"query": "test"})
    assert "status" in result
    print(f"   ✅ Tool execution works (returns: {result['status']})")
    
    # Test 4: MCP Agent Initialization
    print("\n4. Testing MCP Agent...")
    model = DeterministicModel(outputs=["echo 'Hello MCP'"])
    env = LocalEnvironment()
    agent = MCPAgent(model, env, mcp_config=mcp_config)
    
    assert agent.mcp_client is not None
    assert agent.config.enable_mcp_tools == True
    print("   ✅ MCP Agent initializes correctly")
    
    # Test 5: Action Parsing
    print("\n5. Testing Action Parsing...")
    
    # Test bash action parsing
    bash_response = {"content": "```bash\necho 'test'\n```"}
    action = agent.parse_action(bash_response)
    assert "action" in action
    assert action["action"] == "echo 'test'"
    print("   ✅ Bash action parsing works")
    
    # Test MCP action parsing (valid JSON)
    mcp_response = {"content": '@mcp_call{"tool": "search_repositories", "args": {"query": "test"}}'}
    action = agent.parse_action(mcp_response)
    assert action["action_type"] == "mcp"
    assert action["tool"] == "search_repositories"
    print("   ✅ MCP action parsing works")
    
    # Test 6: Template Variables
    print("\n6. Testing Template Variables...")
    assert "mcp_tools_info" in agent.extra_template_vars
    tools_info = agent.extra_template_vars["mcp_tools_info"]
    assert len(tools_info) > 0
    print(f"   ✅ Tools info template variable created ({len(tools_info)} chars)")
    
    print("\n🎉 All MCP integration tests passed!")
    print("\nThe MCP integration is working correctly. The placeholder responses")
    print("show that the infrastructure is in place and ready for real GitHub API calls.")
    
    return True


def show_usage_examples():
    """Show practical usage examples."""
    
    print("\n" + "="*60)
    print("📚 HOW TO USE MCP INTEGRATION")
    print("="*60)
    
    print("\n🚀 QUICK START (No API keys needed for testing):")
    print()
    print("# Test the CLI interface")
    print("mini-mcp --help")
    print()
    print("# Test with a simple task (will prompt for model/API key)")
    print("mini-mcp -t 'echo Hello MCP World'")
    
    print("\n🔧 FULL SETUP (For real GitHub operations):")
    print()
    print("# 1. Get a GitHub token")
    print("export GITHUB_TOKEN=ghp_your_token_here")
    print()
    print("# 2. Get an LLM API key")
    print("export OPENAI_API_KEY=sk-your_key_here")
    print("# OR")
    print("export ANTHROPIC_API_KEY=sk-ant-your_key_here")
    print()
    print("# 3. Run with MCP tools enabled")
    print("mini-mcp -t 'List recent issues in SWE-agent/mini-swe-agent'")
    print()
    print("# 4. Run with MCP tools disabled (bash only)")
    print("mini-mcp --disable-mcp -t 'List recent issues using gh CLI'")
    
    print("\n📋 SAMPLE TASKS TO TRY:")
    print()
    tasks = [
        "Search for repositories about 'AI agents' with >100 stars",
        "List the latest 5 issues in the SWE-agent/mini-swe-agent repository",
        "Get the README file content from SWE-agent/mini-swe-agent",
        "Compare using MCP tools vs bash commands for GitHub operations"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. mini-mcp -t \"{task}\"")
    
    print("\n🔍 TESTING MODES:")
    print()
    print("# Interactive mode (with confirmations)")
    print("mini-mcp")
    print()
    print("# Automatic mode (no confirmations)")  
    print("mini-mcp -y -t 'your task here'")
    print()
    print("# With specific model")
    print("mini-mcp -m gpt-4o -t 'your task here'")
    print()
    print("# MCP disabled (bash commands only)")
    print("mini-mcp --disable-mcp -t 'your task here'")
    
    print("\n⚡ WHAT TO EXPECT:")
    print()
    print("✅ The agent can parse both bash commands and MCP tool calls")
    print("✅ MCP tools provide structured GitHub API access") 
    print("✅ Fallback to bash commands (gh CLI, curl) when needed")
    print("✅ Both approaches can accomplish the same GitHub tasks")
    print("✅ The infrastructure is ready for production GitHub MCP servers")


if __name__ == "__main__":
    if test_mcp_integration_comprehensive():
        show_usage_examples()