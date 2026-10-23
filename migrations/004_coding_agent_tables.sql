-- Phase 5 Migration: Coding Agent Tables & Audit Logs

CREATE TABLE IF NOT EXISTS code_patches (
    id VARCHAR PRIMARY KEY,
    repo_name VARCHAR NOT NULL,
    issue_description TEXT NOT NULL,
    target_files JSONB NOT NULL,
    proposed_patch JSONB NOT NULL,
    diff_summary TEXT NOT NULL,
    branch_name VARCHAR,
    status VARCHAR DEFAULT 'draft',
    approval_id INTEGER REFERENCES approval_requests(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS code_audit_logs (
    id SERIAL PRIMARY KEY,
    patch_id VARCHAR REFERENCES code_patches(id) ON DELETE CASCADE,
    repo_name VARCHAR NOT NULL,
    action_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    static_analysis_results JSONB,
    pr_number INTEGER,
    pr_url VARCHAR,
    triggered_by VARCHAR DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_code_patches_repo ON code_patches(repo_name);
CREATE INDEX IF NOT EXISTS idx_code_audit_logs_repo ON code_audit_logs(repo_name);
