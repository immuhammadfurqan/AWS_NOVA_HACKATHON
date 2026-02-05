/**
 * Shared TypeScript types for AARLP Frontend
 * 
 * Centralized type definitions to avoid duplication across components.
 */

// ============================================================================
// Job Types
// ============================================================================

export interface GeneratedJD {
    job_title: string;
    summary: string;
    description: string;
    responsibilities: string[];
    requirements: string[];
    nice_to_have: string[];
    benefits: string[];
    seo_keywords?: string[];
    salary_range?: string;
    location?: string;
}

export interface JobStatus {
    job_id: string;
    current_node: string;
    jd_approval_status: string;
    has_generated_jd: boolean;
    applicant_count?: number;
    shortlisted_count?: number;
    shortlist_approval_status?: string;
    prescreening_complete?: boolean;
    scheduled_interviews_count?: number;
    error_message?: string;
    created_at?: string;
    updated_at?: string;
}

export interface JobListItem {
    job_id: string;
    role_title: string;
    company_name: string;
    current_node: string;
    created_at: string;
    updated_at: string;
}

export interface JobListResponse {
    jobs: JobListItem[];
    total: number;
}

export interface JobInput {
    role_title: string;
    company_name: string;
    industry: string;
    department?: string;
    key_requirements: string;
    experience_years: number;
    employment_type: 'full_time' | 'part_time' | 'contract' | 'internship';
    location_preference?: string;
    salary_range?: string;
    skills: string[];
    prescreening_questions?: string[];
}

export interface JobCreateResponse {
    job_id: string;
    thread_id: string;
    message: string;
    current_node: string;
}

// ============================================================================
// Auth Types
// ============================================================================

export interface User {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    is_verified: boolean;
    is_superuser: boolean;
    created_at: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    full_name: string;
    is_active?: boolean;
    is_superuser?: boolean;
}

// ============================================================================
// Candidate Types
// ============================================================================

export interface Applicant {
    id: string;
    name: string;
    email: string;
    phone?: string;
    resume_url?: string;
    applied_at: string;
    status: 'new' | 'shortlisted' | 'rejected' | 'interviewing' | 'hired';
    match_score?: number;
}

// ============================================================================
// API Error Types
// ============================================================================

export interface APIError {
    error_code: string;
    message: string;
    details?: Record<string, unknown>;
}
