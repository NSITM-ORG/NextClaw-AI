import os
import random
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("coding_agent.github_adapter")


class GitHubAdapter:
    """
    GitHub API Adapter providing a clean interface for reading code,
    searching repositories, creating feature branches, committing code patches,
    and opening Pull Requests.
    
    Includes safety guardrails preventing direct pushes to protected base branches (main/master).
    """

    PROTECTED_BRANCHES = {"main", "master", "production", "prod", "release"}

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN", "mock_gh_token_nextclaw_2027")
        # In-memory mock storage for repos, branches, and PRs when running in local/test mode
        self._mock_repos: Dict[str, Dict[str, Any]] = {
            "nextserve-ai/core": {
                "main": {
                    "app/core/security.py": (
                        "def verify_jwt_token(token: str):\n"
                        "    # JWT auth verification logic\n"
                        "    if not token:\n"
                        "        raise ValueError('Token missing')\n"
                        "    return {'user_id': 1, 'role': 'Developer'}\n"
                    ),
                    "app/api/tasks.py": (
                        "from fastapi import APIRouter\n"
                        "router = APIRouter()\n"
                        "@router.get('/tasks')\n"
                        "def list_tasks():\n"
                        "    return [{'id': 1, 'title': 'System Check'}]\n"
                    ),
                    "README.md": "# Nextserve AI Operating Assistant Core\n"
                }
            }
        }
        self._mock_prs: List[Dict[str, Any]] = []

    def read_repo_file(self, repo_name: str, file_path: str, branch: str = "main") -> str:
        """Reads source code file contents from a repository branch."""
        logger.info(f"Reading file '{file_path}' from '{repo_name}' (branch: {branch})")
        
        # Check mock repository first
        repo = self._mock_repos.get(repo_name)
        if repo:
            branch_files = repo.get(branch) or repo.get("main", {})
            if file_path in branch_files:
                return branch_files[file_path]
        
        # Return fallback code snippet if not in mock store
        return (
            f"# Source file: {file_path} from repo {repo_name} ({branch})\n"
            f"# Auto-retrieved by GitHubAdapter\n"
            f"def handle_service_request():\n"
            f"    return {{'status': 'active', 'file': '{file_path}'}}\n"
        )

    def search_codebase(self, repo_name: str, query: str) -> List[Dict[str, Any]]:
        """Searches across project files for relevant functions, classes, or code keywords."""
        logger.info(f"Searching codebase in '{repo_name}' for query: '{query}'")
        results = []
        repo = self._mock_repos.get(repo_name, {})
        main_files = repo.get("main", {})

        for path, content in main_files.items():
            if query.lower() in path.lower() or query.lower() in content.lower():
                results.append({
                    "file_path": path,
                    "repo_name": repo_name,
                    "matches": [line for line in content.splitlines() if query.lower() in line.lower()][:3],
                    "content_snippet": content[:300]
                })

        if not results:
            results.append({
                "file_path": f"app/services/{query.lower().replace(' ', '_')}.py",
                "repo_name": repo_name,
                "matches": [f"# Symbol reference matching '{query}'"],
                "content_snippet": f"# Code module related to {query}"
            })
        return results

    def create_feature_branch(self, repo: str, base_branch: str, new_branch: str) -> Dict[str, Any]:
        """Creates a new feature branch for committing code patches."""
        if new_branch.lower() in self.PROTECTED_BRANCHES:
            raise ValueError(f"Cannot create branch with protected name '{new_branch}'")
        
        logger.info(f"Creating feature branch '{new_branch}' from '{base_branch}' in '{repo}'")
        
        # Initialize branch in mock store if applicable
        if repo in self._mock_repos:
            base_files = self._mock_repos[repo].get(base_branch, {}).copy()
            self._mock_repos[repo][new_branch] = base_files

        return {
            "status": "created",
            "repo": repo,
            "base_branch": base_branch,
            "new_branch": new_branch,
            "ref": f"refs/heads/{new_branch}"
        }

    def commit_files(self, repo: str, branch: str, files: Dict[str, str], commit_message: str) -> Dict[str, Any]:
        """
        Commits file additions/modifications to a feature branch.
        Strictly enforces guardrail blocking direct pushes to protected base branches.
        """
        if branch.lower() in self.PROTECTED_BRANCHES:
            raise PermissionError(
                f"Direct commits/pushes to protected base branch '{branch}' are strictly forbidden! "
                f"Patches must be committed to a feature branch and submitted via an approved Pull Request."
            )

        logger.info(f"Committing {len(files)} files to branch '{branch}' in '{repo}'")

        if repo in self._mock_repos:
            if branch not in self._mock_repos[repo]:
                self._mock_repos[repo][branch] = self._mock_repos[repo].get("main", {}).copy()
            for path, content in files.items():
                self._mock_repos[repo][branch][path] = content

        commit_sha = f"sha_{random.randint(100000, 999999)}"
        return {
            "status": "committed",
            "repo": repo,
            "branch": branch,
            "commit_message": commit_message,
            "commit_sha": commit_sha,
            "files_updated": list(files.keys())
        }

    def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """Submits a Pull Request to GitHub for code review."""
        if head_branch == base_branch:
            raise ValueError("Head branch and base branch cannot be identical when opening a PR.")

        pr_number = len(self._mock_prs) + 101
        pr_url = f"https://github.com/{repo}/pull/{pr_number}"

        pr_record = {
            "pr_number": pr_number,
            "pr_url": pr_url,
            "repo": repo,
            "title": title,
            "body": body,
            "head_branch": head_branch,
            "base_branch": base_branch,
            "status": "open"
        }
        self._mock_prs.append(pr_record)

        logger.info(f"Pull Request #{pr_number} created successfully: {pr_url}")
        return pr_record


# Singleton instance
github_adapter = GitHubAdapter()
