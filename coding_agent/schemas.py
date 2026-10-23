from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RepoContext(BaseModel):
    """Context information for a repository file or search query."""
    repo_name: str = Field(..., description="Target repository name (e.g. org/repo)")
    branch: str = Field("main", description="Target branch name")
    file_path: Optional[str] = Field(None, description="Path to file within repo")
    content: Optional[str] = Field(None, description="Source code content")
    language: Optional[str] = Field(None, description="Programming language")


class IssueAnalysisRequest(BaseModel):
    """Payload to analyze a bug report or feature request and generate a plan."""
    repo_name: str = Field(..., json_schema_extra={"example": "nextserve-ai/core"})
    issue_description: str = Field(..., json_schema_extra={"example": "Fix JWT middleware validation failing on expired tokens"})
    file_paths: Optional[List[str]] = Field(default=None, json_schema_extra={"example": ["app/core/security.py"]})
    branch: str = Field("main", description="Base branch to inspect")


class IssueAnalysisResponse(BaseModel):
    """Structured response from issue analysis."""
    repo_name: str
    issue_description: str
    suggested_plan: str
    affected_files: List[str]
    repo_context: List[RepoContext] = Field(default_factory=list)
    status: str = "analysis_completed"


class CodePatchRequest(BaseModel):
    """Payload to generate a code patch for an issue."""
    repo_name: str = Field(..., json_schema_extra={"example": "nextserve-ai/core"})
    issue_description: str = Field(..., json_schema_extra={"example": "Fix JWT middleware expiration error handling"})
    target_files: Dict[str, str] = Field(
        ...,
        description="Dictionary mapping file paths to updated file contents or modification instructions",
        json_schema_extra={"example": {"app/core/security.py": "def verify_jwt(): ..."}}
    )
    branch: str = Field("main", description="Base branch to target")


class PRDiffResponse(BaseModel):
    """Structured response after generating a code patch draft with Level 3 approval status."""
    patch_id: str
    pr_title: str
    diff_summary: str
    target_repo: str
    affected_files: List[str]
    proposed_patch: Dict[str, str]
    branch_name: str
    requires_approval: bool = True
    approval_id: Optional[int] = None
    status: str = "pending_approval"


class SubmitPRRequest(BaseModel):
    """Payload to submit an approved pull request."""
    patch_id: str = Field(..., description="ID of the approved code patch draft")
    repo_name: str = Field(..., json_schema_extra={"example": "nextserve-ai/core"})
    pr_title: Optional[str] = Field(None, json_schema_extra={"example": "fix(auth): handle expired JWT tokens gracefully"})
    pr_body: Optional[str] = Field(None, json_schema_extra={"example": "Resolves issue with JWT middleware token expiry handling."})
    head_branch: Optional[str] = Field(None, description="Feature branch name containing changes")
    base_branch: str = Field("main", description="Target base branch for PR merge")


class PullRequestResult(BaseModel):
    """Result payload after PR submission."""
    patch_id: str
    repo_name: str
    pr_number: int
    pr_url: str
    head_branch: str
    base_branch: str
    status: str = "pr_created"
    static_analysis_results: Dict[str, Any] = Field(default_factory=dict)


class CodeExecutionAudit(BaseModel):
    """Audit record for coding agent actions."""
    id: Optional[int] = None
    patch_id: Optional[str] = None
    repo_name: str
    action_type: str
    status: str
    static_analysis_results: Optional[Dict[str, Any]] = None
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    triggered_by: str = "coding_agent"
    created_at: Optional[str] = None
