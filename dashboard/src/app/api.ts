import type {
  ExperimentRun,
  ModelResult,
  RunSummary,
  ThreadResult,
} from './types';

declare const __API_BASE_URL__: string;

interface ApiClassificationResult {
  state: string | null;
  trajectory: string | null;
  participation_balance: string | null;
  discourse_quality: string | null;
  inquiry_phase: string | null;
  reasoning: string | null;
  confidence: number | null;
}

interface ApiInterventionResult {
  decision: 'intervene' | 'no_intervention' | null;
  role: string | null;
  technique: string | null;
  post_to_thread: boolean | null;
  reasoning: string | null;
  confidence: number | null;
}

interface ApiResponseResult {
  text: string | null;
  reasoning: string | null;
  confidence: number | null;
}

interface ApiThreadResult {
  thread_key: string;
  thread_title: string;
  expected_state: string | null;
  classification: ApiClassificationResult;
  intervention: ApiInterventionResult;
  role_reasoning: string | null;
  role_confidence: number | null;
  response: ApiResponseResult | null;
  duration_ms: number;
  error: string | null;
  logfuse_url?: string | null;
}

interface ApiModelResult {
  model_name: string;
  family: string | null;
  size: string | null;
  threads: Record<string, ApiThreadResult>;
  completion_count: number;
  total_threads: number;
  error_count: number;
  avg_duration_ms: number;
}

interface ApiRunSummary {
  run_id: string;
  run_name: string;
  timestamp: string;
  run_type?: string | null;
  run_kind: string;
  status: string;
  progress_message?: string | null;
  model_count: number;
  thread_count: number;
  total_runs: number;
  completed_runs: number;
  error_count: number;
  avg_duration_ms: number;
  summary_available: boolean;
}

export interface CommentSummary {
  author: string;
  body: string;
}

export interface ThreadDescriptor {
  key: string;
  title: string;
  body: string;
  comments: CommentSummary[];
}

export interface TriggerRunPayload {
  run_name?: string;
  models?: string[];
  threads?: string[];
}

export interface TriggerRunResult {
  run_id: string;
  status: string;
}

interface ApiRunDetail {
  run_id: string;
  run_name: string;
  timestamp: string;
  run_type?: string | null;
  run_kind: string;
  status?: string | null;
  progress_message?: string | null;
  total_runs?: number;
  completed_runs?: number;
  error_count?: number;
  models: Record<string, ApiModelResult>;
  summary_markdown: string | null;
}

function toRunType(value?: string | null): 'experiment' | 'live' {
  return value === 'live' ? 'live' : 'experiment';
}

function toStatus(errorCount: number): RunSummary['status'] {
  if (errorCount === 0) {
    return 'passed';
  }

  return 'unstable';
}

function mapThread(thread: ApiThreadResult): ThreadResult {
  return {
    thread_key: thread.thread_key,
    thread_title: thread.thread_title,
    expected_state: thread.expected_state ?? null,
    classification: {
      state: thread.classification.state ?? 'unknown',
      trajectory: thread.classification.trajectory ?? 'unknown',
      participation_balance:
        thread.classification.participation_balance ?? 'unknown',
      discourse_quality:
        thread.classification.discourse_quality ?? 'unknown',
      inquiry_phase: thread.classification.inquiry_phase ?? 'unknown',
      reasoning: thread.classification.reasoning ?? '',
      confidence: thread.classification.confidence ?? 0,
    },
    intervention: {
      decision: thread.intervention.decision ?? 'no_intervention',
      role: thread.intervention.role ?? undefined,
      technique: thread.intervention.technique ?? undefined,
      post_to_thread: thread.intervention.post_to_thread ?? undefined,
      reasoning: thread.intervention.reasoning ?? undefined,
      confidence: thread.intervention.confidence ?? 0,
    },
    role_reasoning: thread.role_reasoning ?? undefined,
    role_confidence: thread.role_confidence ?? undefined,
    response: thread.response
      ? {
          text: thread.response.text ?? '',
          reasoning: thread.response.reasoning ?? '',
          confidence: thread.response.confidence ?? 0,
        }
      : undefined,
    duration_ms: thread.duration_ms,
    error: thread.error ?? undefined,
    logfuse_url: thread.logfuse_url ?? undefined,
  };
}

function mapModel(model: ApiModelResult): ModelResult {
  const threads = Object.fromEntries(
    Object.entries(model.threads).map(([key, value]) => [key, mapThread(value)])
  );
  const threadValues = Object.values(threads);
  const classificationCorrect = threadValues.filter(
    (thread) =>
      !thread.error
      && Boolean(thread.expected_state)
      && thread.classification.state === thread.expected_state
  ).length;
  const interventionTriggered = threadValues.filter(
    (thread) => !thread.error && thread.intervention.decision === 'intervene'
  ).length;

  return {
    model_name: model.model_name,
    family: model.family ?? 'Unknown',
    size: model.size ?? 'Unknown',
    threads,
    completion_count: model.completion_count,
    total_threads: model.total_threads,
    classification_correct: classificationCorrect,
    intervention_count: interventionTriggered,
    avg_duration: model.avg_duration_ms,
    error_count: model.error_count,
  };
}

export function mapRunSummary(summary: ApiRunSummary): RunSummary {
  return {
    run_id: summary.run_id,
    run_name: summary.run_name,
    timestamp: summary.timestamp,
    run_type: toRunType(summary.run_type),
    run_kind: summary.run_kind,
    status: summary.status === 'running' ? 'running' : summary.status === 'noop' ? 'noop' : toStatus(summary.error_count),
    progress_message: summary.progress_message ?? undefined,
    model_count: summary.model_count,
    thread_count: summary.thread_count,
    total_runs: summary.total_runs,
    completed_runs: summary.completed_runs,
    error_count: summary.error_count,
    avg_duration_ms: summary.avg_duration_ms,
    summary_available: summary.summary_available,
  };
}

export function mapRunDetail(detail: ApiRunDetail): ExperimentRun {
  const computedErrorCount = Object.values(detail.models).reduce(
    (sum, model) => sum + model.error_count,
    0
  );

  return {
    run_id: detail.run_id,
    run_name: detail.run_name,
    timestamp: detail.timestamp,
    run_type: toRunType(detail.run_type),
    run_kind: detail.run_kind,
    status: detail.status === 'running' ? 'running' : detail.status === 'noop' ? 'noop' : toStatus(detail.error_count ?? computedErrorCount),
    progress_message: detail.progress_message ?? undefined,
    total_runs: detail.total_runs,
    completed_runs: detail.completed_runs,
    error_count: detail.error_count,
    models: Object.fromEntries(
      Object.entries(detail.models).map(([key, value]) => [key, mapModel(value)])
    ),
    summary_markdown: detail.summary_markdown ?? undefined,
  };
}

export async function fetchConfig(): Promise<{ lms_url: string }> {
  const response = await fetch(`${__API_BASE_URL__}/health`);
  if (!response.ok) {
    throw new Error('Failed to load config.');
  }
  return response.json();
}

export async function fetchRunSummaries(): Promise<RunSummary[]> {
  const response = await fetch(`${__API_BASE_URL__}/runs`);
  if (!response.ok) {
    throw new Error('Failed to load runs.');
  }

  const payload: ApiRunSummary[] = await response.json();
  return payload.map(mapRunSummary);
}

export async function fetchRunDetail(runId: string): Promise<ExperimentRun> {
  const response = await fetch(`${__API_BASE_URL__}/runs/${runId}`);
  if (!response.ok) {
    throw new Error(`Failed to load run ${runId}.`);
  }

  const payload: ApiRunDetail = await response.json();
  return mapRunDetail(payload);
}

export async function fetchThreads(): Promise<ThreadDescriptor[]> {
  const response = await fetch(`${__API_BASE_URL__}/runs/threads`);
  if (!response.ok) {
    throw new Error('Failed to load available threads.');
  }
  return response.json();
}

export async function fetchEvalModels(): Promise<string[]> {
  const response = await fetch(`${__API_BASE_URL__}/runs/models`);
  if (!response.ok) {
    throw new Error('Failed to load eval models.');
  }
  return response.json();
}

export interface LmsThreadDescriptor {
  id: string;
  course_id: string;
  title: string;
  body: string;
  author: string;
  comment_count: number;
}

export interface ThreadHistoryItem {
  thread_id: string;
  timestamp: string;
  role: string;
  technique: string;
  reasoning: string;
  response_text: string;
}

export async function fetchLmsThreads(courseId: string): Promise<LmsThreadDescriptor[]> {
  const response = await fetch(`${__API_BASE_URL__}/threads/browse?course_id=${encodeURIComponent(courseId)}`);
  if (response.status === 503) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail ?? 'LMS not configured.');
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail ?? 'Failed to load threads.');
  }
  return response.json();
}

export async function triggerRun(
  payload: TriggerRunPayload
): Promise<TriggerRunResult> {
  const response = await fetch(`${__API_BASE_URL__}/runs/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail?.detail ?? 'Failed to trigger run.');
  }
  return response.json();
}

export async function fetchThreadHistory(
  threadId: string
): Promise<ThreadHistoryItem[]> {
  const response = await fetch(
    `${__API_BASE_URL__}/threads/${encodeURIComponent(threadId)}/history`
  );
  if (!response.ok) {
    throw new Error(`Failed to load history for thread ${threadId}.`);
  }
  return response.json();
}