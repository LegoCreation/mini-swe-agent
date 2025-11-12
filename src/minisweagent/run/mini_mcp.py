#!/usr/bin/env python3

"""Run mini-SWE-agent with MCP (Model Context Protocol) support for GitHub operations."""

import os
import traceback
from pathlib import Path
from typing import Any

import typer
import yaml
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console

from minisweagent import global_config_dir
from minisweagent.agents.mcp_agent import MCPAgent
from minisweagent.config import builtin_config_dir, get_config_path
from minisweagent.environments.local import LocalEnvironment
from minisweagent.integrations.github_mcp import MCPToolConfig
from minisweagent.models import get_model
from minisweagent.run.extra.config import configure_if_first_time
from minisweagent.run.utils.save import save_traj
from minisweagent.utils.log import logger

DEFAULT_CONFIG = Path(os.getenv("MSWEA_MCP_CONFIG_PATH", builtin_config_dir / "mcp_agent.yaml"))
DEFAULT_OUTPUT = global_config_dir / "last_mcp_run.traj.json"
console = Console(highlight=False)
app = typer.Typer(rich_markup_mode="rich")
prompt_session = PromptSession(history=FileHistory(global_config_dir / "mcp_task_history.txt"))

_HELP_TEXT = """Run mini-SWE-agent with GitHub MCP (Model Context Protocol) support.

[not dim]
This version of mini-SWE-agent includes GitHub MCP tools for structured
interaction with GitHub repositories, issues, and pull requests.

The agent can use both:
- Traditional bash commands (gh CLI, curl, git)
- GitHub MCP tools for structured operations

[bold green]mini-mcp[/bold green] Run with MCP support
[bold green]mini-mcp -y[/bold green] Run in yolo mode (no confirmations)

More information: [bold green]https://mini-swe-agent.com/latest/[/bold green]
[/not dim]
"""


# fmt: off
@app.command(help=_HELP_TEXT)
def main(
    model_name: str | None = typer.Option(None, "-m", "--model", help="Model to use"),
    model_class: str | None = typer.Option(None, "--model-class", help="Model class to use", rich_help_panel="Advanced"),
    task: str | None = typer.Option(None, "-t", "--task", help="Task/problem statement", show_default=False),
    yolo: bool = typer.Option(False, "-y", "--yolo", help="Run without confirmation"),
    cost_limit: float | None = typer.Option(None, "-l", "--cost-limit", help="Cost limit. Set to 0 to disable."),
    config_spec: Path = typer.Option(DEFAULT_CONFIG, "-c", "--config", help="Path to config file"),
    output: Path | None = typer.Option(DEFAULT_OUTPUT, "-o", "--output", help="Output trajectory file"),
    github_token: str | None = typer.Option(None, "--github-token", help="GitHub token for MCP operations"),
    enable_mcp: bool = typer.Option(True, "--enable-mcp/--disable-mcp", help="Enable or disable MCP tools"),
    exit_immediately: bool = typer.Option(False, "--exit-immediately", help="Exit immediately when agent finishes", rich_help_panel="Advanced"),
) -> Any:
    # fmt: on
    configure_if_first_time()
    
    config_path = get_config_path(config_spec)
    console.print(f"Loading MCP agent config from [bold green]'{config_path}'[/bold green]")
    config = yaml.safe_load(config_path.read_text())

    if not task:
        console.print("[bold yellow]What do you want to do?")
        task = prompt_session.prompt(
            "",
            multiline=True,
            bottom_toolbar=HTML(
                "Submit task: <b fg='yellow' bg='black'>Esc+Enter</b> | "
                "Navigate history: <b fg='yellow' bg='black'>Arrow Up/Down</b> | "
                "Search history: <b fg='yellow' bg='black'>Ctrl+R</b>"
            ),
        )
        console.print("[bold green]Got that, thanks![/bold green]")

    # Apply CLI overrides
    if yolo:
        config.setdefault("agent", {})["mode"] = "yolo"
    if cost_limit is not None:
        config.setdefault("agent", {})["cost_limit"] = cost_limit
    if exit_immediately:
        config.setdefault("agent", {})["confirm_exit"] = False
    if model_class is not None:
        config.setdefault("model", {})["model_class"] = model_class
    
    # MCP-specific config
    config.setdefault("agent", {})["enable_mcp_tools"] = enable_mcp

    # Initialize components
    model = get_model(model_name, config.get("model", {}))
    env = LocalEnvironment(**config.get("env", {}))
    mcp_config = MCPToolConfig(github_token=github_token)

    # Create MCP-aware agent
    agent = MCPAgent(model, env, mcp_config=mcp_config, **config.get("agent", {}))
    
    console.print("[bold green]MCP agent initialized[/bold green]")
    if enable_mcp:
        console.print("[bold yellow]GitHub MCP tools are enabled[/bold yellow]")
    
    exit_status, result, extra_info = None, None, None
    try:
        exit_status, result = agent.run(task)
    except Exception as e:
        logger.error(f"Error running MCP agent: {e}", exc_info=True)
        exit_status, result = type(e).__name__, str(e)
        extra_info = {"traceback": traceback.format_exc()}
    finally:
        if output:
            save_traj(agent, output, exit_status=exit_status, result=result, extra_info=extra_info)
    
    return agent


if __name__ == "__main__":
    app()
