"""GitHub MCP integration for mini-swe-agent.

This module provides a simple wrapper around the GitHub MCP server,
allowing agents to interact with GitHub repositories, issues, and pull requests.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MCPToolConfig:
    """Configuration for MCP tools."""

    github_token: str | None = None
    enabled_tools: list[str] | None = None

    def __post_init__(self):
        if self.github_token is None:
            self.github_token = os.getenv("GITHUB_TOKEN")
        if self.enabled_tools is None:
            self.enabled_tools = [
                "search_repositories",
                "search_code",
                "create_or_update_file",
                "get_file_contents",
                "create_issue",
                "list_issues",
                "create_pull_request",
                "list_commits",
            ]


class GitHubMCPClient:
    """Simple client for GitHub MCP server integration.
    
    This provides a minimal interface to GitHub operations through MCP,
    keeping with mini-swe-agent's philosophy of simplicity.
    """

    def __init__(self, config: MCPToolConfig | None = None):
        self.config = config or MCPToolConfig()
        self._tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize available MCP tools as simple function definitions."""
        self._tools = {
            "search_repositories": {
                "description": "Search for GitHub repositories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "sort": {"type": "string", "enum": ["stars", "forks", "updated"]},
                    },
                    "required": ["query"],
                },
            },
            "search_code": {
                "description": "Search for code in GitHub repositories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Code search query"},
                    },
                    "required": ["query"],
                },
            },
            "get_file_contents": {
                "description": "Get contents of a file from a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "path": {"type": "string", "description": "File path"},
                    },
                    "required": ["owner", "repo", "path"],
                },
            },
            "create_or_update_file": {
                "description": "Create or update a file in a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "message": {"type": "string"},
                        "branch": {"type": "string"},
                    },
                    "required": ["owner", "repo", "path", "content", "message", "branch"],
                },
            },
            "create_issue": {
                "description": "Create a new issue in a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "title": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["owner", "repo", "title"],
                },
            },
            "list_issues": {
                "description": "List issues in a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"]},
                    },
                    "required": ["owner", "repo"],
                },
            },
            "create_pull_request": {
                "description": "Create a new pull request",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "title": {"type": "string"},
                        "head": {"type": "string"},
                        "base": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["owner", "repo", "title", "head", "base"],
                },
            },
            "list_commits": {
                "description": "List commits in a repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "sha": {"type": "string"},
                    },
                    "required": ["owner", "repo"],
                },
            },
        }

    def get_tools(self) -> list[dict]:
        """Return list of available tools in OpenAI function format."""
        return [
            {"type": "function", "function": {"name": name, **tool}}
            for name, tool in self._tools.items()
            if name in self.config.enabled_tools
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool call through MCP.
        
        For now, this returns a simulated response. In production,
        this would connect to the actual GitHub MCP server.
        """
        if tool_name not in self._tools:
            return {"error": f"Unknown tool: {tool_name}"}

        logger.info(f"Executing MCP tool: {tool_name} with args: {arguments}")

        # This is where you'd connect to the actual MCP server
        # For now, return a placeholder that guides the agent to use bash
        return {
            "status": "mcp_placeholder",
            "message": f"MCP tool '{tool_name}' called. In this minimal implementation, "
            f"please use bash commands with gh CLI or curl to accomplish this task instead. "
            f"Arguments received: {json.dumps(arguments, indent=2)}",
        }

    def format_tools_for_prompt(self) -> str:
        """Format available tools as a string for inclusion in prompts."""
        tools = self.get_tools()
        if not tools:
            return ""

        lines = ["Available GitHub MCP Tools:"]
        for tool in tools:
            func = tool["function"]
            lines.append(f"- {func['name']}: {func.get('description', 'No description')}")

        lines.append(
            "\nNote: You can use these tools or standard bash commands (gh, curl, git) to interact with GitHub."
        )
        return "\n".join(lines)
