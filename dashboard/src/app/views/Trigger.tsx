import { useEffect, useState } from 'react';
import { CheckCircle, ChevronDown, ChevronRight, FileText, RefreshCw, Zap } from 'lucide-react';
import {
  fetchConfig,
  fetchEvalModels,
  fetchLmsThreads,
  fetchRunSummaries,
  fetchThreads,
  triggerRun,
  type LmsThreadDescriptor,
  type ThreadDescriptor,
} from '../api';

type ThreadSource = 'fixtures' | 'live';

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

  // Models
  const [models, setModels] = useState<string[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState<string | null>(null);

  // Selection
  const [selectedThreadKeys, setSelectedThreadKeys] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [expandedThreads, setExpandedThreads] = useState<Set<string>>(new Set());

  // Step collapse state (all collapsed by default)
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());
  const toggleStep = (step: number) =>
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });

  // Run
  const [runName, setRunName] = useState('');
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

  // When switching source, reset thread selection
  const handleSourceChange = (src: ThreadSource) => {
    setThreadSource(src);
    setSelectedThreadKeys([]);
    setExpandedThreads(new Set());
    setLmsError(null);
  };

  const fetchLmsThreadsForCourse = async () => {
    if (!courseId.trim()) return;
    setLmsLoading(true);
    setLmsError(null);
    setLmsThreads([]);
    setSelectedThreadKeys([]);
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
        <h2 className="text-2xl mb-6 text-foreground">New build</h2>
        <div className="max-w-lg mx-auto text-center py-16">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg text-foreground mb-2">
            {triggeredRunStatus === 'running' ? 'Run started' : 'Run finished'}
          </h3>
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
            Go to Run History
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-[1000px] mx-auto">
      <div className="mb-6">
        <div className="text-caption uppercase tracking-ui text-muted-foreground mb-2">Pipeline</div>
        <h1 className="text-3xl text-foreground">New build</h1>
      </div>

      {triggerError && (
        <div className="mb-6 rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900">
          {triggerError}
        </div>
      )}

      <div className="space-y-4">
        {/* Step 1: Threads */}
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
            <span className="text-sm font-medium text-foreground">Select threads</span>
            <span className="ml-auto text-xs text-muted-foreground">
              {selectedThreadKeys.length > 0 ? `${selectedThreadKeys.length} selected` : 'none selected'}
            </span>
          </button>
          {expandedSteps.has(1) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              Fixtures include an expected state, so the trace matrix will show correct/incorrect. Live threads come from an active course and show classified state only.
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
                Fixtures
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
                Live
              </button>
            </div>
          </div>

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
                          <span className="text-sm text-foreground">{thread.title}</span>
                          <div className="text-xs text-muted-foreground font-mono mt-0.5">{thread.key}</div>
                        </div>
                        {(thread.body || thread.comments.length > 0) && (
                          <button
                            type="button"
                            onClick={(e) => { e.preventDefault(); toggleExpanded(thread.key); }}
                            className="text-muted-foreground hover:text-foreground flex-shrink-0"
                            title={isExpanded ? 'Collapse conversation' : 'Expand conversation'}
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
                              <p className="mt-1 leading-relaxed line-clamp-4">{thread.body}</p>
                            </div>
                          )}
                          {thread.comments.length > 0 && (
                            <div className="space-y-1.5">
                              <span className="font-medium text-muted-foreground uppercase tracking-wide text-label">
                                {thread.comments.length} comment{thread.comments.length !== 1 ? 's' : ''}
                              </span>
                              {thread.comments.slice(0, 3).map((c, i) => (
                                <div key={i} className="text-xs text-muted-foreground pl-2 border-l-2 border-border">
                                  <span className="font-medium text-foreground">{c.author}:</span>{' '}
                                  <span className="line-clamp-2">{c.body}</span>
                                </div>
                              ))}
                              {thread.comments.length > 3 && (
                                <div className="text-label text-muted-foreground pl-2">
                                  +{thread.comments.length - 3} more comments
                                </div>
                              )}
                            </div>
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
                Live threads do not have an expected state, so the trace matrix will show classified state only (no correct/incorrect comparison).
              </div>
              <form
                className="flex gap-2 mb-4"
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
                  {lmsLoading ? 'Loading...' : 'Fetch'}
                </button>
              </form>
              {lmsError && (
                <p className="text-sm text-red-600 mb-3">{lmsError}</p>
              )}
              {lmsThreads.length > 0 && (
                <div className="space-y-2 mb-4">
                  {lmsThreads.map((thread) => {
                    const isExpanded = expandedThreads.has(thread.id);
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
                              onClick={(e) => { e.preventDefault(); toggleExpanded(thread.id); }}
                              className="text-muted-foreground hover:text-foreground flex-shrink-0"
                              title={isExpanded ? 'Collapse' : 'Expand'}
                            >
                              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                            </button>
                          )}
                        </label>
                        {isExpanded && thread.body && (
                          <div className="border-t border-border px-3 pb-3 pt-2 bg-muted">
                            <span className="font-medium text-muted-foreground uppercase tracking-wide text-label">Opening post</span>
                            <p className="mt-1 text-xs text-muted-foreground leading-relaxed line-clamp-4">{thread.body}</p>
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

        {/* Step 2: Models */}
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
            <span className="text-sm font-medium text-foreground">Select models</span>
            <span className="ml-auto text-xs text-muted-foreground">
              {selectedModels.length > 0 ? `${selectedModels.length} selected` : 'none selected'}
            </span>
          </button>
          {expandedSteps.has(2) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              Available models are configured in the backend. Each selected model runs against every selected thread.
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

        {/* Step 3: Run */}
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
            <span className="text-sm font-medium text-foreground">Run</span>
            <span className="ml-auto text-xs text-muted-foreground">
              {selectedThreadKeys.length} threads · {selectedModels.length} models · {selectedThreadKeys.length * selectedModels.length} checks
            </span>
          </button>
          {expandedSteps.has(3) && (
          <div className="px-6 pb-6 border-t border-border pt-4">
            <p className="text-xs text-muted-foreground mb-4">
              The run starts immediately in the background. Track progress in the run history.
            </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Run name (optional)</label>
              <input
                type="text"
                value={runName}
                onChange={(e) => setRunName(e.target.value)}
                placeholder={`${new Date().toISOString().split('T')[0]} — custom run`}
                className="w-full px-3 py-2 border border-border rounded text-sm"
              />
            </div>

            <div className="p-4 bg-muted rounded text-sm">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <span className="font-medium text-foreground">Summary</span>
              </div>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div>Source: <span className="font-mono">{threadSource}</span></div>
                <div>Threads: <span className="font-mono">{selectedThreadKeys.length}</span></div>
                <div>Models: <span className="font-mono">{selectedModels.length}</span></div>
                <div>Total checks: <span className="font-mono">{selectedThreadKeys.length * selectedModels.length}</span></div>
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
              The run starts immediately in the background. Execution typically takes 2–5 minutes per model per thread.
            </p>
          </div>
          </div>
          )}
        </div>
      </div>
    </div>
  );
}
