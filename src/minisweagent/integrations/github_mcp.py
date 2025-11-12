import requests

class MCPTools:
    def __init__(self, config):
        self.config = config

    def available_tools(self) -> str:
        return """Available MCP tools:
- search_repositories: Search GitHub repositories
- get_file_contents: Get file contents from a repository
- list_issues: List repository issues
- get_commits: Get recent commits from a repository
- list_pull_requests: List pull requests in a repository
- get_contributors: List repository contributors
- get_repo_details: Get detailed repository metadata
- create_issue: Create a new issue in a repository
- list_branches: List branches of a repository
- create_repository: Create a new GitHub repository"""

    def execute_mcp_tool(self, tool: str, args: dict) -> dict:
        """Execute MCP tool via GitHub API."""
        headers = {
            "Authorization": f"Bearer {self.config.github_token}",
            "Accept": "application/vnd.github+json"
        }

        base_url = "https://api.github.com"

        match tool:
            case "search_repositories":
                return requests.get(f"{base_url}/search/repositories", headers=headers, params={"q": args["query"]}).json()
            
            case "get_file_contents":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}/contents/{args['path']}", headers=headers).json()
            
            case "list_issues":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}/issues", headers=headers, params=args.get("params", {})).json()
            
            case "get_commits":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}/commits", headers=headers, params=args.get("params", {})).json()
            
            case "list_pull_requests":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}/pulls", headers=headers, params=args.get("params", {})).json()
            
            case "get_contributors":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}/contributors", headers=headers).json()
            
            case "get_repo_details":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}", headers=headers).json()
            
            case "create_issue":
                data = {
                    "title": args["title"],
                    "body": args.get("body", ""),
                    "assignees": args.get("assignees", [])
                }
                return requests.post(f"{base_url}/repos/{args['owner']}/{args['repo']}/issues", headers=headers, json=data).json()
            
            case "list_branches":
                return requests.get(f"{base_url}/repos/{args['owner']}/{args['repo']}/branches", headers=headers).json()
            
            case "create_repository":
                """
                Create a new GitHub repository for the authenticated user.
                Args:
                    name (str): Repository name (required)
                    description (str): Repository description
                    private (bool): True for private repo
                    auto_init (bool): True to initialize with a README
                """
                data = {
                    "name": args["name"],
                    "description": args.get("description", ""),
                    "private": args.get("private", False),
                    "auto_init": args.get("auto_init", True)
                }
                # For organizations: use POST /orgs/{org}/repos instead
                if "org" in args:
                    url = f"{base_url}/orgs/{args['org']}/repos"
                else:
                    url = f"{base_url}/user/repos"
                return requests.post(url, headers=headers, json=data).json()

            case _:
                return {"error": f"Unknown tool: {tool}"}
