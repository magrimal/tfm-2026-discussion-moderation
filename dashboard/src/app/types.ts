export interface ClassificationResult {
  state: string;
  trajectory: string;
  participation_balance: string;
  discourse_quality: string;
  inquiry_phase: string;
  reasoning: string;
  confidence: number;
}

export interface InterventionResult {
  decision: 'intervene' | 'no_intervention';
  role?: string;
  technique?: string;
  post_to_thread?: boolean;
  reasoning?: string;
  confidence: number;
}

export interface ResponseResult {
  text: string;
  reasoning: string;
  confidence: number;
}

export interface ThreadResult {
  thread_key: string;
  thread_title: string;
  expected_state: string | null;
  classification: ClassificationResult;
  intervention: InterventionResult;
  role_reasoning?: string;
  role_confidence?: number;
  response?: ResponseResult;
  duration_ms: number;
  error?: string;
  logfuse_url?: string;
}

export interface ModelResult {
  model_name: string;
  family: string;
  size: string;
  threads: Record<string, ThreadResult>;
  completion_count: number;
  total_threads: number;
  classification_correct: number;
  intervention_count: number;
  avg_duration: number;
  error_count: number;
}

export interface RunSummary {
  run_id: string;
  run_name: string;
  timestamp: string;
  run_type?: 'experiment' | 'live';
  run_kind?: string;
  status?: 'passed' | 'unstable' | 'failed' | 'running' | 'noop';
  progress_message?: string;
  model_count: number;
  thread_count: number;
  total_runs: number;
  completed_runs: number;
  error_count: number;
  avg_duration_ms: number;
  summary_available: boolean;
}

export interface ExperimentRun {
  run_id: string;
  run_name: string;
  timestamp: string;
  run_type?: 'experiment' | 'live';
  status?: 'passed' | 'unstable' | 'failed' | 'running' | 'noop';
  run_kind?: string;
  progress_message?: string;
  total_runs?: number;
  completed_runs?: number;
  error_count?: number;
  models: Record<string, ModelResult>;
  summary_markdown?: string;
}
