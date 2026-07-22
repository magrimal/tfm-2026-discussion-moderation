import { useEffect, useState } from 'react';
import { CheckCircle, ChevronDown, ChevronRight, FileText, RefreshCw, Zap } from 'lucide-react';
import { WorkflowNote } from '../components/WorkflowNote';
import {
  fetchConfig,
  fetchEvalModels,
  fetchLmsThreadDetail,
  fetchLmsThreads,
  fetchRunSummaries,
  fetchThreads,
  triggerRun,
  type LmsThreadDetail,
  type LmsThreadDescriptor,
  type ThreadDescriptor,
} from '../api';
import { RUN_RETRY_STORAGE_KEY, type RunRetryPayload } from '../types';

const THREAD_PREVIEW_BODY_CHARS = 360;
const THREAD_PREVIEW_COMMENT_COUNT = 2;
const RECENT_RUN_NAMES_KEY = 'facilitation-recent-run-names';
const MAX_RECENT_RUN_NAMES = 20;

type ThreadSource = 'fixtures' | 'live';

function shortModelLabel(model: string): string {
  const withoutProvider = model.includes(':')
    ? model.slice(model.indexOf(':') + 1)
    : model;
  const lastSegment = withoutProvider.includes('/')
    ? withoutProvider.split('/').pop() ?? withoutProvider
    : withoutProvider;
  return lastSegment.replace(/:/g, '-');
}

function defaultRunName(threadCount: number, models: string[]): string {
  if (threadCount === 0 || models.length === 0) {
    return '';
  }
  const modelLabel =
    models.length <= 2
      ? models.map(shortModelLabel).join('+')
      : `${models.length}-models`;
  return `${threadCount}-threads-${modelLabel}`;
}

function loadRecentRunNames(): string[] {
  try {
    const raw = localStorage.getItem(RECENT_RUN_NAMES_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

function saveRecentRunName(name: string) {
  if (!name.trim()) return;
  try {
    const existing = loadRecentRunNames().filter((n) => n !== name);
    const next = [name, ...existing].slice(0, MAX_RECENT_RUN_NAMES);
    localStorage.setItem(RECENT_RUN_NAMES_KEY, JSON.stringify(next));
  } catch {
    // localStorage unavailable (private browsing, quota) - skip silently
  }
}

interface Props {
  onRunTriggered: (runId: string) => void;
}

export function Trigger({ onRunTriggered }: Props) {
  // Fixture threads
  const [fixtureThreads, setFixtureThreads] = useState<ThreadDescriptor[]>([]);
  const [fixtureThreadsLoading, setFixtureThreadsLoading] = useState(true);
  const [fixtureThreadsError, setFixtureThreadsError] = useState<string | null>(null);

  // LMS threads
  const [lmsUrl, setLmsUrl] = useState<string | null>(null);
  const [threadSource, setThreadSource] = useState<ThreadSource>('fixtures');
  const [courseId, setCourseId] = useState('');
  const [lmsThreads, setLmsThreads] = useState<LmsThreadDescriptor[]>([]);
  const [lmsLoading, setLmsLoading] = useState(false);
  const [lmsError, setLmsError] = useState<string | null>(null);
  const [lmsThreadDetails, setLmsThreadDetails] = useState<Record<string, LmsThreadDetail>>({});
  const [lmsThreadDetailsLoading, setLmsThreadDetailsLoading] = useState<Set<string>>(new Set());
  const [lmsThreadDetailsError, setLmsThreadDetailsError] = useState<Record<string, string>>({});

  // Models
  const [models, setModels] = useState<string[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState<string | null>(null);

  // Selection
  const [selectedThreadKeys, setSelectedThreadKeys] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [expandedThreads, setExpandedThreads] = useState<Set<string>>(new Set());
  const [expandedThreadContent, setExpandedThreadContent] = useState<Set<string>>(new Set());

  // Step collapse state (start with step 1 open to guide the flow)
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([1, 2]));
  const toggleStep = (step: number) =>
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });

  // Retry: prefilled from a run's "Retry run" button via sessionStorage.
  // Read synchronously (lazy init) so runName/runNameTouched below start
  // correct on the very first render - reading it in a useEffect instead
  // races the auto-fill-sync effect, which also runs on mount and would
  // stomp the prefilled name back to '' before this one's update lands.
  const [pendingRetry] = useState<RunRetryPayload | null>(() => {
    try {
      const raw = sessionStorage.getItem(RUN_RETRY_STORAGE_KEY);
      return raw ? (JSON.parse(raw) as RunRetryPayload) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    if (pendingRetry) {
      sessionStorage.removeItem(RUN_RETRY_STORAGE_KEY);
    }
    if (pendingRetry?.source === 'live') {
      setThreadSource('live');
    }
    // pendingRetry is set once via lazy init and never changes - this only
    // needs to run on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Run
  const [runName, setRunName] = useState(() => pendingRetry?.runName ?? '');
  const [runNameTouched, setRunNameTouched] = useState(() => pendingRetry !== null);
  const [recentRunNames, setRecentRunNames] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [triggeredRunId, setTriggeredRunId] = useState<string | null>(null);
  const [triggeredRunStatus, setTriggeredRunStatus] = useState<string | null>(null);
  const [triggeredRunProgress, setTriggeredRunProgress] = useState<string | null>(null);
  const [triggeredRunCompleted, setTriggeredRunCompleted] = useState<number | null>(null);
  const [triggeredRunTotal, setTriggeredRunTotal] = useState<number | null>(null);
  const [triggerError, setTriggerError] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig().then((cfg) => setLmsUrl(cfg.lms_url)).catch(() => {});
  }, []);

  useEffect(() => {
    setRecentRunNames(loadRecentRunNames());
  }, []);

  // Keep the run name in sync with the current selection until the user
  // types their own value. Clearing the field manually resumes auto-fill.
  useEffect(() => {
    if (runNameTouched) return;
    setRunName(defaultRunName(selectedThreadKeys.length, selectedModels));
  }, [selectedThreadKeys.length, selectedModels, runNameTouched]);

  useEffect(() => {
    fetchThreads()
      .then((data) => {
        setFixtureThreads(data);
        setSelectedThreadKeys([]);
      })
      .catch((err: Error) => setFixtureThreadsError(err.message))
      .finally(() => setFixtureThreadsLoading(false));
  }, []);

  useEffect(() => {
    fetchEvalModels()
      .then((data) => {
        setModels(data);
        setSelectedModels([]);
      })
      .catch((err: Error) => setModelsError(err.message))
      .finally(() => setModelsLoading(false));
  }, []);

  // Retry: select the previous fixture threads once they're loaded
  useEffect(() => {
    if (!pendingRetry || pendingRetry.source !== 'fixtures') return;
    if (fixtureThreadsLoading) return;
    const available = new Set(fixtureThreads.map((t) => t.key));
    setSelectedThreadKeys(
      pendingRetry.threadKeys.filter((key) => available.has(key))
    );
  }, [pendingRetry, fixtureThreadsLoading, fixtureThreads]);

  // Retry: load the previous course's threads directly (bypasses the
  // courseId input state, which wouldn't be set yet on this render)
  useEffect(() => {
    if (!pendingRetry || pendingRetry.source !== 'live' || !pendingRetry.courseId) {
      return;
    }
    const retryCourseId = pendingRetry.courseId;
    setCourseId(retryCourseId);
    setLmsLoading(true);
    setLmsError(null);
    fetchLmsThreads(retryCourseId)
      .then((data) => {
        setLmsThreads(data);
        const available = new Set(data.map((t) => t.id));
        setSelectedThreadKeys(
          pendingRetry.threadKeys.filter((key) => available.has(key))
        );
      })
      .catch((err: unknown) => {
        setLmsError(err instanceof Error ? err.message : 'Failed to load LMS threads.');
      })
      .finally(() => setLmsLoading(false));
  }, [pendingRetry]);

  // Retry: select the previous models once the model list is loaded
  useEffect(() => {
    if (!pendingRetry || modelsLoading) return;
    const available = new Set(models);
    setSelectedModels(
      pendingRetry.models.filter((model) => available.has(model))
    );
  }, [pendingRetry, modelsLoading, models]);

  useEffect(() => {
    if (selectedThreadKeys.length === 0) {
      return;
    }
    setExpandedSteps((prev) => {
      if (prev.has(3)) {
        return prev;
      }
      const next = new Set(prev);
      next.add(3);
      return next;
    });
  }, [selectedThreadKeys.length]);

  useEffect(() => {
    if (selectedModels.length === 0) {
      return;
    }
    setExpandedSteps((prev) => {
      if (prev.has(4)) {
        return prev;
      }
      const next = new Set(prev);
      next.add(4);
      return next;
    });
  }, [selectedModels.length]);

  // When switching source, reset thread selection
  const handleSourceChange = (src: ThreadSource) => {
    setThreadSource(src);
    setSelectedThreadKeys([]);
    setExpandedThreads(new Set());
    setExpandedThreadContent(new Set());
    setLmsThreadDetails({});
    setLmsThreadDetailsLoading(new Set());
    setLmsThreadDetailsError({});
    setLmsError(null);
    setExpandedSteps((prev) => {
      if (prev.has(2)) {
        return prev;
      }
      const next = new Set(prev);
      next.add(2);
      return next;
    });
  };

  const fetchLmsThreadsForCourse = async () => {
    if (!courseId.trim()) return;
    setLmsLoading(true);
    setLmsError(null);
    setLmsThreads([]);
    setSelectedThreadKeys([]);
    setLmsThreadDetails({});
    setLmsThreadDetailsLoading(new Set());
    setLmsThreadDetailsError({});
    try {
      const data = await fetchLmsThreads(courseId.trim());
      setLmsThreads(data);
      setSelectedThreadKeys([]);
    } catch (err: unknown) {
      setLmsError(err instanceof Error ? err.message : 'Failed to load LMS threads.');
    } finally {
      setLmsLoading(false);
    }
  };

  const toggleThreadKey = (key: string) => {
    setSelectedThreadKeys((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const toggleModel = (model: string) => {
    setSelectedModels((prev) =>
      prev.includes(model) ? prev.filter((m) => m !== model) : [...prev, model]
    );
  };

  const allThreadKeys =
    threadSource === 'fixtures'
      ? fixtureThreads.map((t) => t.key)
      : lmsThreads.map((t) => t.id);
  const allThreadsSelected =
    allThreadKeys.length > 0 && selectedThreadKeys.length === allThreadKeys.length;
  const toggleAllThreads = () =>
    setSelectedThreadKeys(allThreadsSelected ? [] : allThreadKeys);

  const allModelsSelected = models.length > 0 && selectedModels.length === models.length;
  const toggleAllModels = () => setSelectedModels(allModelsSelected ? [] : models);

  const toggleExpanded = (key: string) => {
    setExpandedThreads((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleExpandedContent = (key: string) => {
    setExpandedThreadContent((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const fetchLmsThreadDetailForPreview = async (threadId: string) => {
    if (lmsThreadDetails[threadId]) {
      return;
    }

    setLmsThreadDetailsLoading((prev) => {
      if (prev.has(threadId)) {
        return prev;
      }
      const next = new Set(prev);
      next.add(threadId);
      return next;
    });
    setLmsThreadDetailsError((prev) => {
      if (!prev[threadId]) {
        return prev;
      }
      const next = { ...prev };
      delete next[threadId];
      return next;
    });

    try {
      const detail = await fetchLmsThreadDetail(threadId);
      setLmsThreadDetails((prev) => ({ ...prev, [threadId]: detail }));
    } catch (err: unknown) {
      setLmsThreadDetailsError((prev) => ({
        ...prev,
        [threadId]: err instanceof Error ? err.message : 'Failed to load full discussion.',
      }));
    } finally {
      setLmsThreadDetailsLoading((prev) => {
        const next = new Set(prev);
        next.delete(threadId);
        return next;
      });
    }
  };

  const toggleLiveThreadPreview = async (threadId: string) => {
    const isExpanded = expandedThreads.has(threadId);
    if (isExpanded) {
      toggleExpanded(threadId);
      return;
    }
    toggleExpanded(threadId);
    await fetchLmsThreadDetailForPreview(threadId);
  };

  const truncateText = (text: string, maxChars: number) => {
    if (text.length <= maxChars) {
      return text;
    }
    return `${text.slice(0, maxChars).trimEnd()}...`;
  };

  const handleTriggerRun = async () => {
    if (selectedThreadKeys.length === 0 || selectedModels.length === 0) return;

    setIsRunning(true);
    setTriggerError(null);

    try {
      // For LMS threads, pass the raw thread IDs. The backend needs to
      // support running against LMS thread IDs directly (HU-10 backend work).
      const result = await triggerRun({
        run_name: runName.trim() || undefined,
        models: selectedModels,
        threads: selectedThreadKeys,
      });
      saveRecentRunName(runName.trim());
      setRecentRunNames(loadRecentRunNames());
      setTriggeredRunId(result.run_id);
      setTriggeredRunStatus(result.status);
      setTriggeredRunProgress('Queued for execution...');
      setTriggeredRunCompleted(0);
      setTriggeredRunTotal(selectedThreadKeys.length * selectedModels.length);
    } catch (err: unknown) {
      setTriggerError(err instanceof Error ? err.message : 'Unknown error.');
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (!triggeredRunId) {
      return;
    }

    let isMounted = true;
    const pollStatus = async () => {
      try {
        const runs = await fetchRunSummaries();
        if (!isMounted) {
          return;
        }
        const run = runs.find((entry) => entry.run_id === triggeredRunId);
        if (!run) {
          return;
        }
        setTriggeredRunStatus(run.status ?? null);
        setTriggeredRunProgress(run.progress_message ?? null);
        setTriggeredRunCompleted(run.completed_runs);
        setTriggeredRunTotal(run.total_runs);
      } catch {
        if (isMounted) {
          setTriggeredRunProgress('Waiting for run updates...');
        }
      }
    };

    pollStatus();
    const intervalId = window.setInterval(pollStatus, 2500);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, [triggeredRunId]);

  const activeThreadCount =
    threadSource === 'fixtures' ? fixtureThreads.length : lmsThreads.length;

  if (triggeredRunId) {
    return (
      <div className="p-8">
        <div className="mb-6">
          <div className="text-caption uppercase tracking-ui text-muted-foreground mb-2">Run setup</div>
          <h1 className="text-3xl text-foreground">Create a run</h1>
        </div>
        <div className="max-w-lg mx-auto text-center py-16">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">
            {triggeredRunStatus === 'running' ? 'Run started' : 'Run finished'}
          </h2>
          <p className="text-sm text-muted-foreground mb-3">
            Run <span className="font-mono text-foreground">{triggeredRunId}</span>{' '}
            {triggeredRunStatus === 'running'
              ? 'is running in the background.'
              : 'has finished.'}
          </p>
          <p className="text-sm text-muted-foreground mb-6">
            {triggeredRunProgress ?? 'Preparing run...'}
            {typeof triggeredRunCompleted === 'number'
              && typeof triggeredRunTotal === 'number'
              && triggeredRunTotal > 0
              ? ` (${triggeredRunCompleted}/${triggeredRunTotal})`
              : ''}
          </p>
          <button
            onClick={() => onRunTriggered(triggeredRunId)}
            className="px-6 py-2 bg-dashboard-accent text-white rounded hover:bg-dashboard-accent-strong transition-colors text-sm"
          >
            Go to Runs
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-[1000px] mx-auto">
      <div className="mb-6">
        <div className="text-caption uppercase tracking-ui text-muted-foreground mb-2">Run setup</div>
        <h1 className="text-3xl text-foreground">Create a run</h1>
      </div>

      <WorkflowNote
        title="How to use this page"
        steps={[
          'Choose where the discussions come from: sample data or a live course.',
          'Load or review the available discussions, then select the ones you want to test.',
          'Select the models you want to compare.',
          'Review the summary, then start the run.',
        ]}
      />

      {triggerError && (
        <div className="mb-6 rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900">
          {triggerError}
        </div>
      )}

      <div className="space-y-4">
        {/* Step 1: Source */}
        <div className="bg-background border border-border rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => toggleStep(1)}
            className="w-full flex items-center gap-3 px-6 py-4 hover:bg-muted/30 transition-colors text-left"
          >
            <div className="flex-shrink-0 text-muted-foreground">
              {expandedSteps.has(1) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </div>
            <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-muted text-label font-medium text-muted-foreground">1</span>
            <h2 className="text-base font-semibold text-foreground">Choose source</h2>
            <span className="ml-auto text-xs text-muted-foreground">
              {threadSource === 'fixtures' ? 'sample data' : 'live course'}
            </span>
          </button>
          {expandedSteps.has(1) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              A thread is one discussion with its opening post and replies. Start by choosing where those discussions come from.
            </p>
          <div className="flex items-center justify-between mb-4">
            {threadSource === 'live' && lmsUrl && (
              <span className="text-xs text-muted-foreground">Open edX · {lmsUrl}</span>
            )}
            {!(threadSource === 'live' && lmsUrl) && <span />}
            <div className="flex rounded border border-border overflow-hidden text-xs">
              <button
                type="button"
                onClick={() => handleSourceChange('fixtures')}
                className={`px-3 py-1.5 transition-colors ${
                  threadSource === 'fixtures'
                    ? 'bg-dashboard-accent text-white'
                    : 'bg-background text-muted-foreground hover:bg-muted'
                }`}
              >
                Sample data
              </button>
              <button
                type="button"
                onClick={() => handleSourceChange('live')}
                className={`px-3 py-1.5 border-l border-border transition-colors ${
                  threadSource === 'live'
                    ? 'bg-dashboard-accent text-white'
                    : 'bg-background text-muted-foreground hover:bg-muted'
                }`}
              >
                Live course
              </button>
            </div>
          </div>

          <div className="mb-4 rounded border border-border bg-muted/40 px-3 py-3 text-xs text-muted-foreground">
            {threadSource === 'fixtures'
              ? 'Sample data uses built-in example discussions that come with this project. Use it when you want to explore the dashboard or compare models without connecting to a course.'
              : 'Live course loads real discussion threads from the Open edX course ID you enter below. Use it when you want to test the system with course data.'}
          </div>

          {threadSource === 'live' && (
            <form
              className="flex gap-2"
              onSubmit={(e) => { e.preventDefault(); fetchLmsThreadsForCourse(); }}
            >
              <input
                type="text"
                name="course_id"
                autoComplete="on"
                value={courseId}
                onChange={(e) => setCourseId(e.target.value)}
                placeholder="course-v1:Org+Course+Run"
                className="flex-1 px-3 py-2 border border-border rounded text-sm font-mono"
              />
              <button
                type="submit"
                disabled={!courseId.trim() || lmsLoading}
                className="flex items-center gap-1.5 px-3 py-2 bg-dashboard-accent text-white rounded text-sm hover:bg-dashboard-accent-strong transition-colors disabled:bg-muted disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${lmsLoading ? 'animate-spin' : ''}`} />
                {lmsLoading ? 'Loading...' : 'Load discussions'}
              </button>
            </form>
          )}
          </div>
          )}
        </div>

        {/* Step 2: Threads */}
        <div className="bg-background border border-border rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => toggleStep(2)}
            className="w-full flex items-center gap-3 px-6 py-4 hover:bg-muted/30 transition-colors text-left"
          >
            <div className="flex-shrink-0 text-muted-foreground">
              {expandedSteps.has(2) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </div>
            <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-muted text-label font-medium text-muted-foreground">2</span>
            <h2 className="text-base font-semibold text-foreground">Select threads</h2>
            <span className="ml-auto text-xs text-muted-foreground">
              {selectedThreadKeys.length > 0 ? `${selectedThreadKeys.length} selected` : 'none selected'}
            </span>
          </button>
          {expandedSteps.has(2) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              Review the available discussions and open a thread to read it before selecting the ones you want to test.
            </p>

          {threadSource === 'fixtures' && (
            <>
              {fixtureThreadsLoading && (
                <p className="text-sm text-muted-foreground mb-4">Loading threads...</p>
              )}
              {fixtureThreadsError && (
                <p className="text-sm text-red-600 mb-4">{fixtureThreadsError}</p>
              )}
              <div className="space-y-2 mb-4">
                {fixtureThreads.map((thread) => {
                  const isExpanded = expandedThreads.has(thread.key);
                  const isShowingFullContent = expandedThreadContent.has(thread.key);
                  const hasLongBody = thread.body.length > THREAD_PREVIEW_BODY_CHARS;
                  const hasExtraComments =
                    thread.comments.length > THREAD_PREVIEW_COMMENT_COUNT;
                  const canShowMore = hasLongBody || hasExtraComments;
                  const visibleComments = isShowingFullContent
                    ? thread.comments
                    : thread.comments.slice(0, THREAD_PREVIEW_COMMENT_COUNT);
                  return (
                    <div key={thread.key} className="border border-border rounded">
                      <label className="flex items-center gap-3 p-3 hover:bg-muted cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedThreadKeys.includes(thread.key)}
                          onChange={() => toggleThreadKey(thread.key)}
                          className="w-4 h-4"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span className="text-sm text-foreground">{thread.title}</span>
                            {thread.source && (
                              <span
                                className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                                  thread.source === 'real'
                                    ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                                    : 'bg-muted text-muted-foreground'
                                }`}
                                title={
                                  thread.source === 'real'
                                    ? 'Extracted from a real MOOC dataset (ADR 0041)'
                                    : 'Hand/LLM-authored fixture'
                                }
                              >
                                {thread.source}
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground font-mono mt-0.5">{thread.key}</div>
                        </div>
                        {(thread.body || thread.comments.length > 0) && (
                          <button
                            type="button"
                            onClick={(e) => { e.preventDefault(); toggleExpanded(thread.key); }}
                            className="text-muted-foreground hover:text-foreground flex-shrink-0"
                            title={isExpanded ? 'Hide discussion' : 'Show discussion'}
                          >
                            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                          </button>
                        )}
                      </label>
                      {isExpanded && (
                        <div className="border-t border-border px-3 pb-3 pt-2 space-y-2 bg-muted">
                          {thread.body && (
                            <div className="text-xs text-muted-foreground">
                              <span className="font-medium text-muted-foreground uppercase tracking-wide text-label">Opening post</span>
                              <p className="mt-1 leading-relaxed whitespace-pre-wrap">
                                {isShowingFullContent
                                  ? thread.body
                                  : truncateText(thread.body, THREAD_PREVIEW_BODY_CHARS)}
                              </p>
                            </div>
                          )}
                          {thread.comments.length > 0 && (
                            <div className="space-y-1.5">
                              <span className="font-medium text-muted-foreground uppercase tracking-wide text-label">
                                {thread.comments.length} comment{thread.comments.length !== 1 ? 's' : ''}
                              </span>
                              {visibleComments.map((c, i) => (
                                <div key={i} className="text-xs text-muted-foreground pl-2 border-l-2 border-border">
                                  <span className="font-medium text-foreground">{c.author}:</span>{' '}
                                  <span className="whitespace-pre-wrap">{c.body}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          {canShowMore && (
                            <button
                              type="button"
                              onClick={() => toggleExpandedContent(thread.key)}
                              className="text-xs text-dashboard-accent hover:underline"
                            >
                              {isShowingFullContent ? 'Show less' : 'Show more'}
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {threadSource === 'live' && (
            <>
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
                Live threads do not include reference answers. This preview shows the opening post that is currently available from the course.
              </div>
              {lmsError && (
                <p className="text-sm text-red-600 mb-3">{lmsError}</p>
              )}
              {!lmsLoading && lmsThreads.length === 0 && !lmsError && (
                <p className="text-sm text-muted-foreground mb-3">Load a course in step 1 to see its discussion threads here.</p>
              )}
              {lmsThreads.length > 0 && (
                <div className="space-y-2 mb-4">
                  {lmsThreads.map((thread) => {
                    const isExpanded = expandedThreads.has(thread.id);
                    const isShowingFullContent = expandedThreadContent.has(thread.id);
                    const detailedThread = lmsThreadDetails[thread.id];
                    const detailedComments = detailedThread?.comments ?? [];
                    const isLoadingDetails = lmsThreadDetailsLoading.has(thread.id);
                    const detailError = lmsThreadDetailsError[thread.id];
                    const fullBody = detailedThread?.body || thread.body;
                    const hasLongBody =
                      fullBody.length > THREAD_PREVIEW_BODY_CHARS;
                    const hasExtraComments =
                      detailedComments.length > THREAD_PREVIEW_COMMENT_COUNT;
                    const canShowMore = hasLongBody || hasExtraComments;
                    const visibleComments = isShowingFullContent
                      ? detailedComments
                      : detailedComments.slice(0, THREAD_PREVIEW_COMMENT_COUNT);
                    return (
                      <div key={thread.id} className="border border-border rounded">
                        <label className="flex items-center gap-3 p-3 hover:bg-muted cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedThreadKeys.includes(thread.id)}
                            onChange={() => toggleThreadKey(thread.id)}
                            className="w-4 h-4"
                          />
                          <div className="flex-1 min-w-0">
                            <span className="text-sm text-foreground">{thread.title}</span>
                            <div className="text-xs text-muted-foreground mt-0.5">
                              <span className="font-mono">{thread.id}</span>
                              {thread.author && <span> · {thread.author}</span>}
                              {thread.comment_count > 0 && (
                                <span> · {thread.comment_count} comment{thread.comment_count !== 1 ? 's' : ''}</span>
                              )}
                            </div>
                          </div>
                          {thread.body && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                toggleLiveThreadPreview(thread.id).catch(() => {});
                              }}
                              className="text-muted-foreground hover:text-foreground flex-shrink-0"
                              title={isExpanded ? 'Hide discussion' : 'Show discussion'}
                            >
                              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                            </button>
                          )}
                        </label>
                        {isExpanded && thread.body && (
                          <div className="border-t border-border px-3 pb-3 pt-2 bg-muted space-y-2">
                            <span className="font-medium text-muted-foreground uppercase tracking-wide text-label">Opening post</span>
                            <p className="mt-1 text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">
                              {isShowingFullContent
                                ? fullBody
                                : truncateText(fullBody, THREAD_PREVIEW_BODY_CHARS)}
                            </p>

                            {isLoadingDetails && (
                              <p className="text-xs text-muted-foreground">Loading full discussion...</p>
                            )}

                            {!isLoadingDetails && detailError && (
                              <div className="text-xs text-red-600">
                                <p>{detailError}</p>
                                <button
                                  type="button"
                                  className="mt-1 text-dashboard-accent hover:underline"
                                  onClick={() => {
                                    fetchLmsThreadDetailForPreview(thread.id).catch(() => {});
                                  }}
                                >
                                  Try again
                                </button>
                              </div>
                            )}

                            {!isLoadingDetails && !detailError && detailedComments.length > 0 && (
                              <div className="space-y-1.5">
                                <span className="font-medium text-muted-foreground uppercase tracking-wide text-label">
                                  {detailedComments.length} repl{detailedComments.length === 1 ? 'y' : 'ies'}
                                </span>
                                {visibleComments.map((comment, index) => (
                                  <div
                                    key={`${thread.id}-comment-${index}`}
                                    className="text-xs text-muted-foreground border-l-2 border-border"
                                    style={{
                                      marginLeft: `${(comment.depth ?? 0) * 10}px`,
                                      paddingLeft: '8px',
                                    }}
                                  >
                                    <span className="font-medium text-foreground">{comment.author}:</span>{' '}
                                    <span className="whitespace-pre-wrap">{comment.body}</span>
                                  </div>
                                ))}
                              </div>
                            )}

                            {canShowMore && (
                              <button
                                type="button"
                                onClick={() => toggleExpandedContent(thread.id)}
                                className="mt-2 text-xs text-dashboard-accent hover:underline"
                              >
                                {isShowingFullContent ? 'Show less' : 'Show more'}
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{selectedThreadKeys.length} of {activeThreadCount} thread(s) selected</span>
            {activeThreadCount > 0 && (
              <button
                type="button"
                onClick={toggleAllThreads}
                className="text-dashboard-accent hover:underline"
              >
                {allThreadsSelected ? 'Deselect all' : 'Select all'}
              </button>
            )}
          </div>
          </div>
          )}
        </div>

        {/* Step 3: Models */}
        <div className="bg-background border border-border rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => toggleStep(3)}
            className="w-full flex items-center gap-3 px-6 py-4 hover:bg-muted/30 transition-colors text-left"
          >
            <div className="flex-shrink-0 text-muted-foreground">
              {expandedSteps.has(3) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </div>
            <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-muted text-label font-medium text-muted-foreground">3</span>
            <h2 className="text-base font-semibold text-foreground">Select models</h2>
            <span className="ml-auto text-xs text-muted-foreground">
              {selectedModels.length > 0 ? `${selectedModels.length} selected` : 'none selected'}
            </span>
          </button>
          {expandedSteps.has(3) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              Select one or more models for the selected threads.
            </p>

          {modelsLoading && (
            <p className="text-sm text-muted-foreground mb-4">Loading models...</p>
          )}
          {modelsError && (
            <p className="text-sm text-red-600 mb-4">{modelsError}</p>
          )}

          <div className="space-y-2 mb-4">
            {models.map((model) => (
              <label
                key={model}
                className="flex items-center gap-3 p-3 border border-border rounded hover:bg-muted cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedModels.includes(model)}
                  onChange={() => toggleModel(model)}
                  className="w-4 h-4"
                />
                <span className="font-mono text-sm">{model}</span>
              </label>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{selectedModels.length} model(s) selected</span>
            {models.length > 0 && (
              <button
                type="button"
                onClick={toggleAllModels}
                className="text-dashboard-accent hover:underline"
              >
                {allModelsSelected ? 'Deselect all' : 'Select all'}
              </button>
            )}
          </div>
          </div>
          )}
        </div>

        {/* Step 4: Run */}
        <div className="bg-background border border-border rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => toggleStep(4)}
            className="w-full flex items-center gap-3 px-6 py-4 hover:bg-muted/30 transition-colors text-left"
          >
            <div className="flex-shrink-0 text-muted-foreground">
              {expandedSteps.has(4) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </div>
            <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-muted text-label font-medium text-muted-foreground">4</span>
            <h2 className="text-base font-semibold text-foreground">Start run</h2>
            <span className="ml-auto text-xs text-muted-foreground">
              {selectedThreadKeys.length} threads · {selectedModels.length} models · {selectedThreadKeys.length * selectedModels.length} comparisons
            </span>
          </button>
          {expandedSteps.has(4) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              Review the summary, then start the run.
            </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Run name (optional)</label>
              <input
                type="text"
                value={runName}
                onChange={(e) => {
                  const { value } = e.target;
                  setRunName(value);
                  setRunNameTouched(value.trim() !== '');
                }}
                list="run-name-history"
                placeholder={`${new Date().toISOString().split('T')[0]} - custom run`}
                className="w-full px-3 py-2 border border-border rounded text-sm"
              />
              {recentRunNames.length > 0 && (
                <datalist id="run-name-history">
                  {recentRunNames.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </datalist>
              )}
            </div>

            <div className="p-4 bg-muted rounded text-sm">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold text-foreground">Summary</h3>
              </div>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div>Source: <span className="font-mono">{threadSource === 'fixtures' ? 'sample data' : 'live course'}</span></div>
                <div>Threads: <span className="font-mono">{selectedThreadKeys.length}</span></div>
                <div>Models: <span className="font-mono">{selectedModels.length}</span></div>
                <div>Total comparisons: <span className="font-mono">{selectedThreadKeys.length * selectedModels.length}</span></div>
              </div>
            </div>

            <button
              onClick={handleTriggerRun}
              disabled={
                isRunning ||
                selectedThreadKeys.length === 0 ||
                selectedModels.length === 0 ||
                fixtureThreadsLoading ||
                modelsLoading
              }
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-dashboard-accent text-white rounded hover:bg-dashboard-accent-strong transition-colors disabled:bg-muted disabled:cursor-not-allowed"
            >
              {isRunning ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Starting run...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Trigger run
                </>
              )}
            </button>

            <p className="text-xs text-muted-foreground text-center">
              The run starts immediately, and progress appears in Runs.
            </p>
          </div>
          </div>
          )}
        </div>
      </div>
    </div>
  );
}
