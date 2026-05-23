import { useEffect, useState } from 'react';
import { CheckCircle, ChevronDown, ChevronRight, FileText, RefreshCw, Zap } from 'lucide-react';
import {
  fetchEvalModels,
  fetchLmsThreads,
  fetchRunSummaries,
  fetchThreads,
  triggerRun,
  type LmsThreadDescriptor,
  type ThreadDescriptor,
} from '../api';

type ThreadSource = 'fixtures' | 'lms';

interface Props {
  onRunTriggered: (runId: string) => void;
}

export function Trigger({ onRunTriggered }: Props) {
  // Fixture threads
  const [fixtureThreads, setFixtureThreads] = useState<ThreadDescriptor[]>([]);
  const [fixtureThreadsLoading, setFixtureThreadsLoading] = useState(true);
  const [fixtureThreadsError, setFixtureThreadsError] = useState<string | null>(null);

  // LMS threads
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
    fetchThreads()
      .then((data) => {
        setFixtureThreads(data);
        setSelectedThreadKeys(data.map((t) => t.key));
      })
      .catch((err: Error) => setFixtureThreadsError(err.message))
      .finally(() => setFixtureThreadsLoading(false));
  }, []);

  useEffect(() => {
    fetchEvalModels()
      .then((data) => {
        setModels(data);
        setSelectedModels(data);
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
      setSelectedThreadKeys(data.map((t) => t.id));
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
        <h2 className="text-2xl mb-6 text-gray-900">Trigger Run</h2>
        <div className="max-w-lg mx-auto text-center py-16">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg text-gray-900 mb-2">
            {triggeredRunStatus === 'running' ? 'Run started' : 'Run finished'}
          </h3>
          <p className="text-sm text-gray-600 mb-3">
            Run <span className="font-mono text-gray-800">{triggeredRunId}</span>{' '}
            {triggeredRunStatus === 'running'
              ? 'is running in the background.'
              : 'has finished.'}
          </p>
          <p className="text-sm text-gray-600 mb-6">
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
    <div className="p-8">
      <h2 className="text-2xl mb-6 text-gray-900">Trigger Run</h2>

      {triggerError && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900">
          {triggerError}
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column: Thread Selection */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-300 rounded p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg text-gray-900">Select Threads</h3>
              {/* Source toggle */}
              <div className="flex rounded border border-gray-200 overflow-hidden text-xs">
                <button
                  type="button"
                  onClick={() => handleSourceChange('fixtures')}
                  className={`px-3 py-1.5 transition-colors ${
                    threadSource === 'fixtures'
                      ? 'bg-dashboard-accent text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Fixtures
                </button>
                <button
                  type="button"
                  onClick={() => handleSourceChange('lms')}
                  className={`px-3 py-1.5 border-l border-gray-200 transition-colors ${
                    threadSource === 'lms'
                      ? 'bg-dashboard-accent text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  LMS
                </button>
              </div>
            </div>

            {threadSource === 'fixtures' && (
              <>
                {fixtureThreadsLoading && (
                  <p className="text-sm text-gray-500">Loading threads...</p>
                )}
                {fixtureThreadsError && (
                  <p className="text-sm text-red-600">{fixtureThreadsError}</p>
                )}
                <div className="space-y-2 mb-4">
                  {fixtureThreads.map((thread) => {
                    const isExpanded = expandedThreads.has(thread.key);
                    return (
                      <div key={thread.key} className="border border-gray-200 rounded">
                        <label className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedThreadKeys.includes(thread.key)}
                            onChange={() => toggleThreadKey(thread.key)}
                            className="w-4 h-4"
                          />
                          <div className="flex-1 min-w-0">
                            <span className="text-sm text-gray-900">{thread.title}</span>
                            <div className="text-xs text-gray-500 font-mono mt-0.5">{thread.key}</div>
                          </div>
                          {(thread.body || thread.comments.length > 0) && (
                            <button
                              type="button"
                              onClick={(e) => { e.preventDefault(); toggleExpanded(thread.key); }}
                              className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                              title={isExpanded ? 'Collapse conversation' : 'Expand conversation'}
                            >
                              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                            </button>
                          )}
                        </label>
                        {isExpanded && (
                          <div className="border-t border-gray-100 px-3 pb-3 pt-2 space-y-2 bg-gray-50">
                            {thread.body && (
                              <div className="text-xs text-gray-700">
                                <span className="font-medium text-gray-500 uppercase tracking-wide text-[10px]">Opening post</span>
                                <p className="mt-1 leading-relaxed line-clamp-4">{thread.body}</p>
                              </div>
                            )}
                            {thread.comments.length > 0 && (
                              <div className="space-y-1.5">
                                <span className="font-medium text-gray-500 uppercase tracking-wide text-[10px]">
                                  {thread.comments.length} comment{thread.comments.length !== 1 ? 's' : ''}
                                </span>
                                {thread.comments.slice(0, 3).map((c, i) => (
                                  <div key={i} className="text-xs text-gray-600 pl-2 border-l-2 border-gray-200">
                                    <span className="font-medium text-gray-700">{c.author}:</span>{' '}
                                    <span className="line-clamp-2">{c.body}</span>
                                  </div>
                                ))}
                                {thread.comments.length > 3 && (
                                  <div className="text-[10px] text-gray-400 pl-2">
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

            {threadSource === 'lms' && (
              <>
                <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
                  LMS threads do not have an expected state, so the trace matrix will show classified state only (no correct/incorrect comparison).
                </div>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={courseId}
                    onChange={(e) => setCourseId(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') fetchLmsThreadsForCourse(); }}
                    placeholder="course-v1:Org+Course+Run"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm font-mono"
                  />
                  <button
                    type="button"
                    onClick={fetchLmsThreadsForCourse}
                    disabled={!courseId.trim() || lmsLoading}
                    className="flex items-center gap-1.5 px-3 py-2 bg-dashboard-accent text-white rounded text-sm hover:bg-dashboard-accent-strong transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${lmsLoading ? 'animate-spin' : ''}`} />
                    {lmsLoading ? 'Loading...' : 'Fetch'}
                  </button>
                </div>
                {lmsError && (
                  <p className="text-sm text-red-600 mb-3">{lmsError}</p>
                )}
                {lmsThreads.length > 0 && (
                  <div className="space-y-2 mb-4">
                    {lmsThreads.map((thread) => {
                      const isExpanded = expandedThreads.has(thread.id);
                      return (
                        <div key={thread.id} className="border border-gray-200 rounded">
                          <label className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={selectedThreadKeys.includes(thread.id)}
                              onChange={() => toggleThreadKey(thread.id)}
                              className="w-4 h-4"
                            />
                            <div className="flex-1 min-w-0">
                              <span className="text-sm text-gray-900">{thread.title}</span>
                              <div className="text-xs text-gray-500 mt-0.5">
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
                                className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                                title={isExpanded ? 'Collapse' : 'Expand'}
                              >
                                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                              </button>
                            )}
                          </label>
                          {isExpanded && thread.body && (
                            <div className="border-t border-gray-100 px-3 pb-3 pt-2 bg-gray-50">
                              <span className="font-medium text-gray-500 uppercase tracking-wide text-[10px]">Opening post</span>
                              <p className="mt-1 text-xs text-gray-700 leading-relaxed line-clamp-4">{thread.body}</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            )}

            <div className="text-xs text-gray-600">
              {selectedThreadKeys.length} of {activeThreadCount} thread(s) selected
            </div>
          </div>
        </div>

        {/* Right Column: Model Selection & Trigger */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-300 rounded p-6">
            <h3 className="text-lg mb-4 text-gray-900">Select Models</h3>

            {modelsLoading && (
              <p className="text-sm text-gray-500">Loading models...</p>
            )}
            {modelsError && (
              <p className="text-sm text-red-600">{modelsError}</p>
            )}

            <div className="space-y-2 mb-4">
              {models.map((model) => (
                <label
                  key={model}
                  className="flex items-center gap-3 p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
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

            <div className="text-xs text-gray-600">
              {selectedModels.length} model(s) selected
            </div>
          </div>

          <div className="bg-white border border-gray-300 rounded p-6">
            <h3 className="text-lg mb-4 text-gray-900">Run Configuration</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-700 mb-2">Run Name (optional)</label>
                <input
                  type="text"
                  value={runName}
                  onChange={(e) => setRunName(e.target.value)}
                  placeholder={`${new Date().toISOString().split('T')[0]} — custom run`}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>

              <div className="p-4 bg-gray-50 rounded text-sm">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-700">Run Summary</span>
                </div>
                <div className="space-y-1 text-gray-600">
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
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-dashboard-accent text-white rounded hover:bg-dashboard-accent-strong transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isRunning ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Starting run...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Trigger Run
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
            <div className="flex items-start gap-2">
              <div className="text-blue-600 mt-0.5">ℹ</div>
              <div>
                <div className="font-medium mb-1">Pipeline execution</div>
                <div className="text-blue-800">
                  The run starts immediately in the background. Check the run history to track progress.
                  Execution typically takes 2–5 minutes per model per thread.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
