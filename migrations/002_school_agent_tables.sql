-- Phase 3 Migration: School Agent Tables
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(50) UNIQUE NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL DEFAULT 3,
    description TEXT,
    prerequisites TEXT,
    instructor VARCHAR(255),
    schedule VARCHAR(255),
    tuition NUMERIC(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);
CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department);

-- 2. FAQs and Policies Table
CREATE TABLE IF NOT EXISTS faqs_and_policies (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL, -- 'tuition', 'policy', 'admissions', 'grading', etc.
    question_or_topic VARCHAR(255) NOT NULL,
    answer_or_policy TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs_and_policies(category);

-- 3. School Knowledge Vectors Table (1536 dims for text-embedding-3-small)
CREATE TABLE IF NOT EXISTS school_knowledge_vectors (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL, -- 'course', 'faq', 'policy', 'doc'
    reference_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    text_content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_skv_content_type ON school_knowledge_vectors(content_type);
CREATE INDEX IF NOT EXISTS idx_skv_reference_id ON school_knowledge_vectors(reference_id);

-- Optional HNSW cosine distance index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_skv_embedding_hnsw 
ON school_knowledge_vectors 
USING hnsw (embedding vector_cosine_ops);
