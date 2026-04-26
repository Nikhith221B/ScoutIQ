/* eslint-disable react/no-unescaped-entities */
'use client'

import { useMemo, useState } from 'react'
import type { PipelineShortlistItem, RunPipelineResponse } from './api/client'
import { ingestCandidatesFile, ingestResumeText, runPipeline } from './api/client'

const SAMPLE_JDS: Array<{ id: string; label: string; jd: string }> = [
    {
        id: 'fullstack',
        label: 'Full‑Stack (React + FastAPI)',
        jd: `Role: Full-Stack Engineer (React + FastAPI)

We are looking for a Full-Stack Engineer to build recruiter-facing tools and APIs.

Required:
- React / TypeScript
- Python (FastAPI preferred)
- SQL (PostgreSQL)
- REST APIs
- Git

Preferred:
- Docker
- AWS
- Tailwind CSS

Experience: 3-6 years
Location: Bengaluru (Hybrid)`,
    },
    {
        id: 'data',
        label: 'Data Engineer (Python + SQL)',
        jd: `Role: Data Engineer

Required:
- Python
- SQL
- ETL / pipelines
- Airflow or similar orchestration

Preferred:
- Spark / PySpark
- AWS / GCP
- Data modeling

Experience: 4+ years
Location: Remote`,
    },
    {
        id: 'datasci',
        label: 'Data Scientist (ML + Python)',
        jd: `Role: Data Scientist

We are looking for a Data Scientist to build predictive models and deliver decision-ready insights.

Required:
- Python
- Statistics / probability
- Machine Learning
- SQL
- Experimentation (A/B testing)
- Data analysis & visualization

Preferred:
- Deep learning (PyTorch / TensorFlow)
- NLP
- Feature engineering
- MLOps basics (model monitoring)

Experience: 3-6 years
Location: Remote / Hybrid`,
    },
    {
        id: 'backend',
        label: 'Backend (Django/FastAPI)',
        jd: `Role: Backend Engineer

Required:
- Python
- Django or FastAPI
- PostgreSQL
- Redis
- API design

Preferred:
- Kubernetes
- Observability (logs/metrics/traces)

Experience: 5+ years
Location: Hyderabad (Onsite)`,
    },
]

function pillClass(kind: 'good' | 'warn' | 'bad') {
    if (kind === 'good') return 'bg-green-50 text-green-700 ring-green-200'
    if (kind === 'warn') return 'bg-amber-50 text-amber-700 ring-amber-200'
    return 'bg-rose-50 text-rose-700 ring-rose-200'
}

function scorePill(score: number) {
    const kind = score >= 80 ? 'good' : score >= 65 ? 'warn' : 'bad'
    return `inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${pillClass(kind)}`
}

function safeList(v: unknown): string[] {
    return Array.isArray(v) ? v.filter((x) => typeof x === 'string') : []
}

function Landing() {
    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                {/* Hero Section */}
                <div className="text-center">
                    <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                        <span className="block">AI-Powered Talent</span>
                        <span className="block text-primary-600">Scouting & Engagement Agent</span>
                    </h1>
                    <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                        Intelligent platform for discovering, evaluating, and engaging top talent using AI-powered insights.
                    </p>
                    <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
                        <div className="rounded-md shadow">
                            <a
                                href="#features"
                                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10"
                            >
                                Get Started
                            </a>
                        </div>
                        <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                            <a
                                href="#about"
                                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 md:py-4 md:text-lg md:px-10"
                            >
                                Learn More
                            </a>
                        </div>
                    </div>
                </div>

                {/* Features Section */}
                <div id="features" className="mt-32">
                    <div className="text-center">
                        <h2 className="text-base text-primary-600 font-semibold tracking-wide uppercase">Features</h2>
                        <p className="mt-2 text-3xl leading-8 font-bold tracking-tight text-gray-900 sm:text-4xl">
                            Everything you need to find top talent
                        </p>
                    </div>

                    <div className="mt-10">
                        <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-3">
                            {/* Feature 1 */}
                            <div className="p-6 bg-white rounded-lg shadow-md">
                                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                                    <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-medium text-gray-900">AI-Powered Search</h3>
                                <p className="mt-2 text-base text-gray-500">
                                    Intelligent candidate matching using advanced AI algorithms to find the perfect fit.
                                </p>
                            </div>

                            {/* Feature 2 */}
                            <div className="p-6 bg-white rounded-lg shadow-md">
                                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                                    <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-medium text-gray-900">Smart Engagement</h3>
                                <p className="mt-2 text-base text-gray-500">
                                    Automated outreach and engagement workflows to connect with candidates effectively.
                                </p>
                            </div>

                            {/* Feature 3 */}
                            <div className="p-6 bg-white rounded-lg shadow-md">
                                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                                    <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-medium text-gray-900">Analytics Dashboard</h3>
                                <p className="mt-2 text-base text-gray-500">
                                    Comprehensive insights and analytics to track recruitment performance and metrics.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Status Section */}
                <div id="about" className="mt-32 bg-white rounded-lg shadow-md p-8">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">System Status</h2>
                        <div className="flex items-center justify-center gap-2">
                            <span className="h-3 w-3 bg-green-500 rounded-full"></span>
                            <span className="text-gray-600">All systems operational</span>
                        </div>
                        <p className="mt-4 text-gray-500">
                            Backend API: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:8000</code>
                        </p>
                    </div>
                </div>
            </div>
        </main>
    )
}

export default function Home() {
    const [jdText, setJdText] = useState<string>(SAMPLE_JDS[0]?.jd ?? '')
    const [candidateLimit, setCandidateLimit] = useState<number>(20)
    const [isRunning, setIsRunning] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<RunPipelineResponse | null>(null)
    const [selected, setSelected] = useState<PipelineShortlistItem | null>(null)
    const [uploadedCandidates, setUploadedCandidates] = useState<any[] | null>(null)
    const [ingestError, setIngestError] = useState<string | null>(null)
    const [resumeText, setResumeText] = useState<string>('')
    const [isIngesting, setIsIngesting] = useState(false)

    const parsed = result?.final_output?.parsed_jd
    const shortlist = result?.final_output?.shortlist ?? []
    const weights = result?.final_output?.scoring_weights ?? { match_score_weight: 0.65, interest_score_weight: 0.35 }

    const requiredSkills = useMemo(
        () => safeList(parsed?.required_skills).map((s) => s.toLowerCase().trim()),
        [parsed?.required_skills]
    )

    async function onRun() {
        setIsRunning(true)
        setError(null)
        setResult(null)
        setSelected(null)
        try {
            const res = await runPipeline({
                raw_jd: jdText,
                candidate_limit: candidateLimit,
                candidates_override: uploadedCandidates,
            })
            setResult(res)
            if (res.status !== 'completed') {
                setError('Pipeline did not complete successfully. Check backend logs / stages output.')
            }
        } catch (e: any) {
            setError(e?.message ?? 'Failed to run pipeline')
        } finally {
            setIsRunning(false)
        }
    }

    async function onUploadCandidatesFile(file: File) {
        setIsIngesting(true)
        setIngestError(null)
        try {
            const res = await ingestCandidatesFile(file)
            setUploadedCandidates(res.candidates ?? [])
        } catch (e: any) {
            setIngestError(e?.message ?? 'Failed to ingest file')
            setUploadedCandidates(null)
        } finally {
            setIsIngesting(false)
        }
    }

    async function onParseResumeText() {
        setIsIngesting(true)
        setIngestError(null)
        try {
            const res = await ingestResumeText({ resume_text: resumeText })
            const cands = res.candidates ?? []
            setUploadedCandidates(cands)
            if (!cands.length) setIngestError('No candidate extracted from resume text.')
        } catch (e: any) {
            setIngestError(e?.message ?? 'Failed to parse resume text')
            setUploadedCandidates(null)
        } finally {
            setIsIngesting(false)
        }
    }

    function derivedSkillsMatched(item: PipelineShortlistItem) {
        const direct = safeList(item.matched_skills)
        if (direct.length) return direct
        const cand = safeList(item.skills).map((s) => s.toLowerCase().trim())
        return requiredSkills.filter((s) => cand.includes(s))
    }

    function derivedMissingRequired(item: PipelineShortlistItem) {
        const direct = safeList(item.missing_required_skills)
        if (direct.length) return direct
        const cand = safeList(item.skills).map((s) => s.toLowerCase().trim())
        return requiredSkills.filter((s) => !cand.includes(s))
    }

    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                <div className="flex items-start justify-between gap-6">
                    <div>
                        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900">Recruiter Dashboard</h1>
                        <p className="mt-1 text-sm text-gray-600">
                            Paste a job description, run the pipeline, and review a ranked shortlist with outreach context.
                        </p>
                    </div>
                    <div className="hidden sm:flex items-center gap-2 rounded-lg bg-white px-3 py-2 shadow-sm ring-1 ring-gray-200">
                        <span className="h-2.5 w-2.5 rounded-full bg-green-500" />
                        <span className="text-sm text-gray-700">Dashboard</span>
                    </div>
                </div>

                <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
                    <section className="lg:col-span-5">
                        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
                            <div className="p-5 border-b border-gray-100">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-sm font-semibold text-gray-900">Job Description</h2>
                                    <div className="flex items-center gap-2">
                                        <label className="text-xs text-gray-500">Candidate limit</label>
                                        <input
                                            type="number"
                                            min={1}
                                            max={50}
                                            value={candidateLimit}
                                            onChange={(e) => setCandidateLimit(Number(e.target.value || 20))}
                                            className="w-20 rounded-md border border-gray-200 bg-white px-2 py-1 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                        />
                                    </div>
                                </div>
                                <p className="mt-1 text-xs text-gray-500">
                                    Use the sample buttons or paste your own JD. Then run{' '}
                                    <code className="px-1 py-0.5 rounded bg-gray-50 ring-1 ring-gray-200">/api/run-pipeline</code>.
                                </p>
                            </div>
                            <div className="p-5">
                                <textarea
                                    value={jdText}
                                    onChange={(e) => setJdText(e.target.value)}
                                    placeholder="Paste the job description here…"
                                    className="h-72 w-full resize-none rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />

                                <div className="mt-4 flex flex-wrap gap-2">
                                    {SAMPLE_JDS.map((s) => (
                                        <button
                                            key={s.id}
                                            type="button"
                                            onClick={() => setJdText(s.jd)}
                                            className="rounded-full bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-700 ring-1 ring-inset ring-gray-200 hover:bg-gray-100"
                                        >
                                            {s.label}
                                        </button>
                                    ))}
                                </div>

                                <div className="mt-5 flex items-center gap-3">
                                    <button
                                        type="button"
                                        onClick={onRun}
                                        disabled={isRunning || !jdText.trim()}
                                        className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isRunning ? 'Running…' : 'Run pipeline'}
                                    </button>
                                    {error ? (
                                        <div className="text-sm text-rose-600">{error}</div>
                                    ) : result ? (
                                        <div className="text-sm text-gray-600">
                                            Completed in <span className="font-medium text-gray-900">{result.total_duration_ms}ms</span>
                                        </div>
                                    ) : (
                                        <div className="text-sm text-gray-500">Ready when you are.</div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
                            <div className="p-5 border-b border-gray-100">
                                <h2 className="text-sm font-semibold text-gray-900">Bring your own candidates</h2>
                                <p className="mt-1 text-xs text-gray-500">
                                    Optional. Upload a <span className="font-medium">CSV/JSON</span> or paste resume text. If provided, the pipeline will
                                    match against your uploaded candidates instead of the built-in dataset.
                                </p>
                            </div>
                            <div className="p-5 space-y-4">
                                <div className="flex items-center gap-3">
                                    <input
                                        type="file"
                                        accept=".csv,.json,.pdf"
                                        disabled={isIngesting}
                                        onChange={(e) => {
                                            const f = e.target.files?.[0]
                                            if (f) void onUploadCandidatesFile(f)
                                        }}
                                        className="block w-full text-sm text-gray-700 file:mr-4 file:rounded-lg file:border-0 file:bg-gray-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-gray-700 hover:file:bg-gray-100"
                                    />
                                </div>

                                <div>
                                    <div className="text-xs font-medium text-gray-500">Or paste resume text</div>
                                    <textarea
                                        value={resumeText}
                                        onChange={(e) => setResumeText(e.target.value)}
                                        placeholder="Paste resume text here (skills like Python/React/SQL will be extracted)…"
                                        className="mt-2 h-32 w-full resize-none rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    />
                                    <div className="mt-2 flex items-center gap-3">
                                        <button
                                            type="button"
                                            onClick={onParseResumeText}
                                            disabled={isIngesting || !resumeText.trim()}
                                            className="inline-flex items-center justify-center rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {isIngesting ? 'Parsing…' : 'Create candidate from resume'}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setUploadedCandidates(null)
                                                setIngestError(null)
                                            }}
                                            className="text-sm font-medium text-gray-600 hover:text-gray-900"
                                        >
                                            Clear
                                        </button>
                                    </div>
                                </div>

                                {ingestError ? <div className="text-sm text-rose-600">{ingestError}</div> : null}

                                <div className="rounded-lg bg-gray-50 p-3 ring-1 ring-inset ring-gray-200">
                                    <div className="text-xs font-medium text-gray-500">Status</div>
                                    <div className="mt-1 text-sm text-gray-800">
                                        {uploadedCandidates?.length
                                            ? `Using ${uploadedCandidates.length} uploaded candidate(s) for matching.`
                                            : 'Using built-in candidate dataset.'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {result?.stages?.length ? (
                            <div className="mt-6 rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
                                <div className="p-5 border-b border-gray-100">
                                    <h2 className="text-sm font-semibold text-gray-900">Pipeline stages</h2>
                                </div>
                                <div className="p-5">
                                    <ul className="space-y-3">
                                        {result.stages.map((s, idx) => (
                                            <li key={`${s.stage_name}-${idx}`} className="flex items-center justify-between gap-3">
                                                <div className="min-w-0">
                                                    <div className="text-sm font-medium text-gray-900">{s.stage_name}</div>
                                                    {s.error ? <div className="text-xs text-rose-600 truncate">{s.error}</div> : null}
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <span
                                                        className={`text-xs font-medium ${
                                                            s.status === 'completed'
                                                                ? 'text-green-700'
                                                                : s.status === 'failed'
                                                                ? 'text-rose-700'
                                                                : 'text-gray-600'
                                                        }`}
                                                    >
                                                        {s.status}
                                                    </span>
                                                    <span className="text-xs text-gray-500 tabular-nums">
                                                        {typeof s.duration_ms === 'number' ? `${s.duration_ms}ms` : ''}
                                                    </span>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ) : null}
                    </section>

                    <section className="lg:col-span-7 space-y-6">
                        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
                            <div className="p-5 border-b border-gray-100">
                                <h2 className="text-sm font-semibold text-gray-900">Parsed JD summary</h2>
                                <p className="mt-1 text-xs text-gray-500">This is taken from the pipeline’s parsed JD output.</p>
                            </div>
                            <div className="p-5">
                                {!parsed ? (
                                    <div className="text-sm text-gray-500">Run the pipeline to see the parsed JD summary.</div>
                                ) : (
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        <div className="rounded-lg bg-gray-50 p-4 ring-1 ring-inset ring-gray-200">
                                            <div className="text-xs font-medium text-gray-500">Title</div>
                                            <div className="mt-1 text-sm font-semibold text-gray-900">{parsed.title ?? '—'}</div>
                                            <div className="mt-3 text-xs font-medium text-gray-500">Company</div>
                                            <div className="mt-1 text-sm text-gray-900">{parsed.company ?? '—'}</div>
                                            <div className="mt-3 text-xs font-medium text-gray-500">Experience</div>
                                            <div className="mt-1 text-sm text-gray-900">{parsed.experience_range ?? '—'}</div>
                                        </div>
                                        <div className="rounded-lg bg-gray-50 p-4 ring-1 ring-inset ring-gray-200">
                                            <div className="text-xs font-medium text-gray-500">Required skills</div>
                                            <div className="mt-2 flex flex-wrap gap-1.5">
                                                {safeList(parsed.required_skills).length ? (
                                                    safeList(parsed.required_skills).map((s) => (
                                                        <span
                                                            key={s}
                                                            className="inline-flex items-center rounded-full bg-white px-2 py-0.5 text-xs text-gray-700 ring-1 ring-inset ring-gray-200"
                                                        >
                                                            {s}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span className="text-sm text-gray-500">—</span>
                                                )}
                                            </div>
                                            <div className="mt-4 text-xs font-medium text-gray-500">Preferred skills</div>
                                            <div className="mt-2 flex flex-wrap gap-1.5">
                                                {safeList(parsed.preferred_skills).length ? (
                                                    safeList(parsed.preferred_skills).map((s) => (
                                                        <span
                                                            key={s}
                                                            className="inline-flex items-center rounded-full bg-white px-2 py-0.5 text-xs text-gray-700 ring-1 ring-inset ring-gray-200"
                                                        >
                                                            {s}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span className="text-sm text-gray-500">—</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
                            <div className="p-5 border-b border-gray-100">
                                <div className="flex items-center justify-between gap-4">
                                    <div>
                                        <h2 className="text-sm font-semibold text-gray-900">Ranked shortlist</h2>
                                        <p className="mt-1 text-xs text-gray-500">Click a row to open candidate details.</p>
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        Weights: <span className="font-medium text-gray-900">{weights.match_score_weight}</span> match /{' '}
                                        <span className="font-medium text-gray-900">{weights.interest_score_weight}</span> interest
                                    </div>
                                </div>
                            </div>
                            <div className="p-0 overflow-x-auto">
                                {!shortlist.length ? (
                                    <div className="p-5 text-sm text-gray-500">Run the pipeline to get a ranked shortlist.</div>
                                ) : (
                                    <table className="min-w-full divide-y divide-gray-100">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Candidate</th>
                                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Title</th>
                                                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">Match</th>
                                                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">Interest</th>
                                                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">Combined</th>
                                                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Recommendation</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100 bg-white">
                                            {shortlist.map((c) => (
                                                <tr key={c.candidate_id} onClick={() => setSelected(c)} className="cursor-pointer hover:bg-gray-50">
                                                    <td className="px-4 py-3">
                                                        <div className="text-sm font-medium text-gray-900">{c.candidate_name}</div>
                                                        <div className="text-xs text-gray-500">{c.location ?? ''}</div>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-gray-700">{c.candidate_title}</td>
                                                    <td className="px-4 py-3 text-right">
                                                        <span className={scorePill(c.match_score)}>{c.match_score.toFixed(2)}</span>
                                                    </td>
                                                    <td className="px-4 py-3 text-right">
                                                        <span className={scorePill(c.interest_score)}>{c.interest_score.toFixed(2)}</span>
                                                    </td>
                                                    <td className="px-4 py-3 text-right">
                                                        <span className={scorePill(c.combined_score)}>{c.combined_score.toFixed(2)}</span>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <span className="text-sm font-medium text-gray-900">{c.final_recommendation}</span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    </section>
                </div>
            </div>

            {selected ? (
                <div className="fixed inset-0 z-50">
                    <div className="absolute inset-0 bg-gray-900/40" onClick={() => setSelected(null)} />
                    <div className="absolute inset-y-0 right-0 w-full max-w-2xl bg-white shadow-2xl ring-1 ring-black/5">
                        <div className="flex items-start justify-between gap-4 border-b border-gray-100 p-5">
                            <div className="min-w-0">
                                <div className="text-sm text-gray-500">Candidate</div>
                                <div className="mt-1 text-lg font-semibold text-gray-900 truncate">{selected.candidate_name}</div>
                                <div className="mt-1 text-sm text-gray-700">{selected.candidate_title}</div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setSelected(null)}
                                className="rounded-lg p-2 text-gray-500 hover:bg-gray-50 hover:text-gray-700"
                                aria-label="Close"
                            >
                                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        <div className="h-full overflow-y-auto p-5 pb-10 space-y-6">
                            <div className="grid grid-cols-3 gap-3">
                                <div className="rounded-lg bg-gray-50 p-3 ring-1 ring-inset ring-gray-200">
                                    <div className="text-xs text-gray-500">Match</div>
                                    <div className="mt-1 text-sm font-semibold text-gray-900">{selected.match_score.toFixed(2)}</div>
                                </div>
                                <div className="rounded-lg bg-gray-50 p-3 ring-1 ring-inset ring-gray-200">
                                    <div className="text-xs text-gray-500">Interest</div>
                                    <div className="mt-1 text-sm font-semibold text-gray-900">{selected.interest_score.toFixed(2)}</div>
                                </div>
                                <div className="rounded-lg bg-gray-50 p-3 ring-1 ring-inset ring-gray-200">
                                    <div className="text-xs text-gray-500">Combined</div>
                                    <div className="mt-1 text-sm font-semibold text-gray-900">{selected.combined_score.toFixed(2)}</div>
                                </div>
                            </div>

                            <div className="rounded-xl bg-white ring-1 ring-gray-200">
                                <div className="border-b border-gray-100 p-4">
                                    <div className="text-sm font-semibold text-gray-900">Summary</div>
                                    <div className="mt-1 text-xs text-gray-500">Quick explainability for recruiter review.</div>
                                </div>
                                <div className="p-4 space-y-3">
                                    <div className="text-sm text-gray-800">
                                        <span className="font-medium">Recommendation:</span> {selected.final_recommendation}
                                    </div>
                                    {selected.match_explanation ? (
                                        <div className="text-sm text-gray-700">
                                            <span className="font-medium">Match:</span> {selected.match_explanation}
                                        </div>
                                    ) : null}
                                    {selected.interest_explanation ? (
                                        <div className="text-sm text-gray-700">
                                            <span className="font-medium">Interest:</span> {selected.interest_explanation}
                                        </div>
                                    ) : null}
                                    {selected.recruiter_explanation ? (
                                        <div className="rounded-lg bg-gray-50 p-3 ring-1 ring-inset ring-gray-200 text-sm text-gray-800 space-y-1.5">
                                            <div>
                                                <span className="font-medium">Why matched:</span> {selected.recruiter_explanation.why_matched}
                                            </div>
                                            <div>
                                                <span className="font-medium">Missing:</span> {selected.recruiter_explanation.missing_requirements}
                                            </div>
                                            <div>
                                                <span className="font-medium">Interest:</span> {selected.recruiter_explanation.interest_signal}
                                            </div>
                                            <div>
                                                <span className="font-medium">Summary:</span> {selected.recruiter_explanation.recommendation_summary}
                                            </div>
                                        </div>
                                    ) : null}
                                    {selected.conversation_preview ? (
                                        <div className="text-sm text-gray-700">
                                            <span className="font-medium">Conversation preview:</span> {selected.conversation_preview}
                                        </div>
                                    ) : null}
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="rounded-xl bg-white ring-1 ring-gray-200">
                                    <div className="border-b border-gray-100 p-4">
                                        <div className="text-sm font-semibold text-gray-900">Skills matched</div>
                                    </div>
                                    <div className="p-4">
                                        <div className="flex flex-wrap gap-1.5">
                                            {derivedSkillsMatched(selected).length ? (
                                                derivedSkillsMatched(selected).map((s) => (
                                                    <span
                                                        key={s}
                                                        className="inline-flex items-center rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-700 ring-1 ring-inset ring-green-200"
                                                    >
                                                        {s}
                                                    </span>
                                                ))
                                            ) : (
                                                <span className="text-sm text-gray-500">—</span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="rounded-xl bg-white ring-1 ring-gray-200">
                                    <div className="border-b border-gray-100 p-4">
                                        <div className="text-sm font-semibold text-gray-900">Missing required skills</div>
                                    </div>
                                    <div className="p-4">
                                        <div className="flex flex-wrap gap-1.5">
                                            {derivedMissingRequired(selected).length ? (
                                                derivedMissingRequired(selected).map((s) => (
                                                    <span
                                                        key={s}
                                                        className="inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-700 ring-1 ring-inset ring-amber-200"
                                                    >
                                                        {s}
                                                    </span>
                                                ))
                                            ) : (
                                                <span className="text-sm text-gray-500">—</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="rounded-xl bg-white ring-1 ring-gray-200">
                                <div className="border-b border-gray-100 p-4">
                                    <div className="text-sm font-semibold text-gray-900">Score breakdown</div>
                                </div>
                                <div className="p-4 space-y-2 text-sm text-gray-700">
                                    <div className="flex items-center justify-between">
                                        <span>Match score</span>
                                        <span className="font-medium tabular-nums">{selected.match_score.toFixed(2)}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>Interest score</span>
                                        <span className="font-medium tabular-nums">{selected.interest_score.toFixed(2)}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>
                                            Combined = match × {weights.match_score_weight} + interest × {weights.interest_score_weight}
                                        </span>
                                        <span className="font-semibold tabular-nums text-gray-900">{selected.combined_score.toFixed(2)}</span>
                                    </div>
                                    {selected.match_score_breakdown && Object.keys(selected.match_score_breakdown).length ? (
                                        <div className="pt-2 text-xs text-gray-500">
                                            Match dimensions:{' '}
                                            {Object.entries(selected.match_score_breakdown)
                                                .map(([k, v]) => `${k.replace('_', ' ')}=${Number(v).toFixed(0)}`)
                                                .join(' · ')}
                                        </div>
                                    ) : null}
                                </div>
                            </div>

                            <div className="rounded-xl bg-white ring-1 ring-gray-200">
                                <div className="border-b border-gray-100 p-4">
                                    <div className="text-sm font-semibold text-gray-900">Outreach</div>
                                </div>
                                <div className="p-4 space-y-3">
                                    <div>
                                        <div className="text-xs font-medium text-gray-500">Outreach message</div>
                                        <div className="mt-1 whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm text-gray-800 ring-1 ring-inset ring-gray-200">
                                            {selected.outreach_message ?? '—'}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-xs font-medium text-gray-500">Simulated candidate response</div>
                                        <div className="mt-1 whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm text-gray-800 ring-1 ring-inset ring-gray-200">
                                            {selected.candidate_response ?? '—'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="rounded-xl bg-white ring-1 ring-gray-200">
                                <div className="border-b border-gray-100 p-4">
                                    <div className="text-sm font-semibold text-gray-900">Explanations</div>
                                </div>
                                <div className="p-4 space-y-2 text-sm text-gray-700">
                                    <div>
                                        <div className="text-xs font-medium text-gray-500">Match explanation</div>
                                        <div className="mt-1">{selected.match_explanation ?? '—'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs font-medium text-gray-500">Interest explanation</div>
                                        <div className="mt-1">{selected.interest_explanation ?? '—'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs font-medium text-gray-500">Recruiter-friendly summary</div>
                                        <div className="mt-1 space-y-1.5">
                                            <div>
                                                <span className="font-medium">Why matched:</span>{' '}
                                                {selected.recruiter_explanation?.why_matched ?? '—'}
                                            </div>
                                            <div>
                                                <span className="font-medium">Missing:</span>{' '}
                                                {selected.recruiter_explanation?.missing_requirements ?? '—'}
                                            </div>
                                            <div>
                                                <span className="font-medium">Interest:</span>{' '}
                                                {selected.recruiter_explanation?.interest_signal ?? '—'}
                                            </div>
                                            <div>
                                                <span className="font-medium">Summary:</span>{' '}
                                                {selected.recruiter_explanation?.recommendation_summary ?? '—'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ) : null}
        </main>
    )
}