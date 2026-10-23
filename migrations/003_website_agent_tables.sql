-- Phase 4 Migration: Website Agent Tables & Deployment Audit Logs

-- 1. Website Drafts Table
CREATE TABLE IF NOT EXISTS website_drafts (
    id VARCHAR(100) PRIMARY KEY,
    slug VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    page_type VARCHAR(100) DEFAULT 'general' NOT NULL,
    seo_metadata JSONB,
    status VARCHAR(50) DEFAULT 'pending_approval' NOT NULL, -- 'draft', 'pending_approval', 'approved', 'published', 'rejected'
    preview_url VARCHAR(500),
    approval_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_website_drafts_slug ON website_drafts(slug);
CREATE INDEX IF NOT EXISTS idx_website_drafts_status ON website_drafts(status);

-- 2. Deployment Audit Logs Table
CREATE TABLE IF NOT EXISTS deployment_audit_logs (
    id SERIAL PRIMARY KEY,
    draft_id VARCHAR(100) NOT NULL,
    environment VARCHAR(50) DEFAULT 'production' NOT NULL, -- 'staging', 'production', 'preview'
    status VARCHAR(50) DEFAULT 'success' NOT NULL, -- 'success', 'failed', 'rolled_back'
    preflight_results JSONB,
    deployment_url VARCHAR(500),
    triggered_by VARCHAR(100) DEFAULT 'website_agent' NOT NULL,
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_deployment_audit_draft_id ON deployment_audit_logs(draft_id);
CREATE INDEX IF NOT EXISTS idx_deployment_audit_status ON deployment_audit_logs(status);
