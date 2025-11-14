import json
import os
import re
from dataclasses import dataclass, field
from typing import Literal

from minisweagent.integrations.github_mcp import GithubMCPTools
from minisweagent.integrations.mcp_tools import MCPTools
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console
from typing import Dict

from minisweagent import global_config_dir
from dotenv import load_dotenv
from minisweagent.agents.interactive import InteractiveAgent, InteractiveAgentConfig

console = Console(highlight=False)
prompt_session = PromptSession(history=FileHistory(global_config_dir / "interactive_history.txt"))
load_dotenv()

@dataclass
class MCPAgentConfig(InteractiveAgentConfig):
    enable_mcp_tools: bool = True
    mcp_tool_choice: Literal["auto", "manual"] = "auto"
    github_token: str = field(default_factory=lambda: os.environ.get("GITHUB_TOKEN", ""))


class MCPAgent(InteractiveAgent):
    def __init__(self, *args, config_class=MCPAgentConfig, **kwargs):
        super().__init__(*args, config_class=config_class, **kwargs)

        self.mcp_toolkits: Dict[str, MCPTools] = {
            "github": GithubMCPTools(self.config),
        }

        if self.config.enable_mcp_tools:
            advertised = []
            for name, toolkit in self.mcp_toolkits.items():
                tools = toolkit.available_tools()
                advertised.extend([f"{name}:{tools}"])
            self.extra_template_vars["mcp_tools_info"] = "\n".join(advertised)
        else:
            self.extra_template_vars["mcp_tools_info"] = ""

    def parse_action(self, response: dict) -> dict:
        if self.config.enable_mcp_tools and (mcp_match := re.search(r"@mcp_call(\{.*\})", response["content"], re.DOTALL)):
            call_data = json.loads(mcp_match.group(1))
            raw_tool = call_data["tool"]
            if ":" in raw_tool:
                provider, tool_name = raw_tool.split(":", 1)
            else:
                provider, tool_name = "github", raw_tool
            return {"action_type": "mcp", "provider": provider, "tool": tool_name, "args": call_data.get("args", {}), **response}
        return super().parse_action(response)

    def execute_action(self, action: dict) -> dict:
        if action.get("action_type") != "mcp":
            return super().execute_action(action)
        provider = action.get("provider", "github")
        toolkit = self.mcp_toolkits.get(provider)
        if toolkit is None:
            return {"output": json.dumps({"error": f"Unknown MCP provider '{provider}'"}, indent=2), "exit_code": 1}
        try:
            result = toolkit.execute_mcp_tool(action["tool"], action["args"])
            return {"output": json.dumps(result, indent=2), "exit_code": 0}
        except Exception as e:
            return {"output": json.dumps({"error": str(e)}, indent=2), "exit_code": 1}
    
    def __del__(self):
        pass