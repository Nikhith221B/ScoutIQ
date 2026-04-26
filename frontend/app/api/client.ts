const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface RunPipelineRequest {
    raw_jd: string;
    company?: string | null;
    job_title?: string | null;
    candidate_limit?: number;
    candidates_override?: Array<Record<string, any>> | null;
}

export interface PipelineShortlistItem {
    candidate_id: string;
    candidate_name: string;
    candidate_title: string;
    location?: string;
    skills: string[];
    match_score: number;
    interest_score: number;
    combined_score: number;
    final_recommendation: string;
    match_explanation?: string;
    interest_explanation?: string;
    conversation_preview?: string;
    matched_skills?: string[];
    missing_required_skills?: string[];
    match_score_breakdown?: Record<string, number>;
    interest_breakdown?: Record<string, number>;
    interest_label?: string | null;
    recruiter_explanation?: {
        why_matched: string;
        missing_requirements: string;
        interest_signal: string;
        recommendation_summary: string;
    };
    outreach_message?: string | null;
    candidate_response?: string | null;
}

export interface RunPipelineResponse {
    pipeline_id: string;
    status: string;
    stages: Array<{
        stage_name: string;
        status: string;
        duration_ms?: number;
        output?: any;
        error?: string;
    }>;
    final_output: {
        parsed_jd?: {
            title?: string;
            company?: string;
            required_skills?: string[];
            preferred_skills?: string[];
            experience_range?: string;
        };
        shortlist?: PipelineShortlistItem[];
        scoring_weights?: {
            match_score_weight: number;
            interest_score_weight: number;
        };
        [k: string]: any;
    };
    total_duration_ms: number;
    started_at: string;
    completed_at: string;
}

export interface Talent {
    id: string;
    name: string;
    email: string;
    phone: string;
    skills: string[];
    experience_years: number;
    location: string;
    status: string;
    created_at: string;
}

export async function fetchTalents(): Promise<Talent[]> {
    const response = await fetch(`${API_URL}/api/talents`, {
        cache: 'no-store',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch talents');
    }

    return response.json();
}

export async function fetchTalent(id: string): Promise<Talent> {
    const response = await fetch(`${API_URL}/api/talents/${id}`, {
        cache: 'no-store',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch talent');
    }

    return response.json();
}

export async function checkHealth(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch(`${API_URL}/api/health`);

    if (!response.ok) {
        throw new Error('Failed to check health');
    }

    return response.json();
}

export async function runPipeline(payload: RunPipelineRequest): Promise<RunPipelineResponse> {
    const response = await fetch(`${API_URL}/api/run-pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const text = await response.text().catch(() => '');
        throw new Error(text || `Pipeline request failed (${response.status})`);
    }

    return response.json();
}

export async function ingestCandidatesFile(file: File): Promise<{ source: string; total: number; candidates: any[] }> {
    const form = new FormData();
    form.append('file', file);
    const response = await fetch(`${API_URL}/api/ingest-candidates/file`, {
        method: 'POST',
        body: form,
    });
    if (!response.ok) {
        const text = await response.text().catch(() => '');
        throw new Error(text || `Ingest failed (${response.status})`);
    }
    return response.json();
}

export async function ingestResumeText(payload: {
    resume_text: string;
    name?: string | null;
    title?: string | null;
    location?: string | null;
    years_experience?: number | null;
}): Promise<{ source: string; total: number; candidates: any[] }> {
    const response = await fetch(`${API_URL}/api/ingest-candidates/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const text = await response.text().catch(() => '');
        throw new Error(text || `Ingest failed (${response.status})`);
    }
    return response.json();
}