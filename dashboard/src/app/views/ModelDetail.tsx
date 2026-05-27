import { useCallback, useEffect, useState } from 'react';
import { ModelResult } from '../types';
import { ChevronDown, ChevronRight, ExternalLink } from 'lucide-react';
import { getScenarioDescriptors } from '../scenarios';
import { fetchThreadHistory, type ThreadHistoryItem } from '../api';

interface ModelDetailProps {
  model: ModelResult;
  runId: string;
  runName: string;
  onBackToRunOverview: () => void;
  onBackToHistory: () => void;
}

export function ModelDetail({
  model,
  runId,
  runName,
  onBackToRunOverview,
  onBackToHistory,
}: ModelDetailProps) {
  const [expandedThread, setExpandedThread] = useState<string | null>(null);
  const [expandedMessages, setExpandedMessages] = useState<string | null>(null);
  const [historyByThread, setHistoryByThread] = useState<
    Record<string, ThreadHistoryItem[]>
  >({});
  const [historyLoadingByThread, setHistoryLoadingByThread] = useState<
    Record<string, boolean>
  >({});
  const [historyErrorsByThread, setHistoryErrorsByThread] = useState<
    Record<string, string>
  >({});
  const expectedComparableCount = Object.values(model.threads).filter(
    (thread) => !thread.error && Boolean(thread.expected_state)
  ).length;
  const hasExpectedState = expectedComparableCount > 0;
  const scenarios = getScenarioDescriptors(
    Object.values(model.threads).map(
      (thread) => thread.expected_state || thread.thread_key
    )
  );

  const toggleThread = (threadKey: string) => {
    setExpandedThread(expandedThread === threadKey ? null : threadKey);
  };

  const loadHistoryForThread = useCallback(
    (threadKey: string, force = false) => {
      if (!force && Object.prototype.hasOwnProperty.call(historyByThread, threadKey)) {
        return;
      }
      if (historyLoadingByThread[threadKey]) {
        return;
      }

      setHistoryLoadingByThread((prev) => ({
        ...prev,
        [threadKey]: true,
      }));
      setHistoryErrorsByThread((prev) => {
        const next = { ...prev };
        delete next[threadKey];
        return next;
      });

      fetchThreadHistory(threadKey)
        .then((items) => {
          setHistoryByThread((prev) => ({ ...prev, [threadKey]: items }));
        })
        .catch((error: unknown) => {
          setHistoryErrorsByThread((prev) => ({
            ...prev,
            [threadKey]: (
              error instanceof Error
                ? error.message
                : 'Failed to load thread history.'
            ),
          }));
        })
        .finally(() => {
          setHistoryLoadingByThread((prev) => ({
            ...prev,
            [threadKey]: false,
          }));
        });
    },
    [historyByThread, historyLoadingByThread]
  );

  useEffect(() => {
    if (!expandedThread) {
      return;
    }
    const thread = Object.values(model.threads).find(
      (item) => (item.expected_state || item.thread_key) === expandedThread
    );
    if (!thread) {
      return;
    }

    const threadKey = thread.thread_key;
    loadHistoryForThread(threadKey);
  }, [expandedThread, loadHistoryForThread, model.threads]);

  const renderThreadCard = (scenario: { key: string; label: string }) => {
    const thread = Object.values(model.threads).find(
      (item) => (item.expected_state || item.thread_key) === scenario.key
    );
    if (!thread) return null;

    const isExpanded = expandedThread === scenario.key;

    return (
      <div
        key={scenario.key}
        className={`bg-white border ${thread.error ? 'border-l-4 border-l-red-600' : 'border-gray-200'} rounded-xl p-5 cursor-pointer hover:shadow-lg transition-all shadow-sm`}
        onClick={() => toggleThread(scenario.key)}
      >
        <div className="mb-3 flex items-start justify-between">
          <div>
            <h4 className="font-medium text-gray-900">{thread.thread_title || scenario.label}</h4>
            {thread.expected_state && (
              <div className="text-xs font-mono text-gray-500 mt-0.5">expected: {thread.expected_state}</div>
            )}
          </div>
          {thread.logfuse_url && (
            <a
              href={thread.logfuse_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-gradient-to-r from-dashboard-accent to-dashboard-accent-strong text-white hover:shadow-md rounded-lg transition-all"
            >
              LogFuse
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>

        {thread.error ? (
          <div className="text-sm text-red-700">{thread.error}</div>
        ) : (
          <>
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-xs border border-gray-200">
                <div className={`w-2 h-2 rounded-full ${
                  thread.expected_state
                    ? (thread.classification.state === thread.expected_state
                      ? 'bg-green-600'
                      : 'bg-yellow-500')
                    : 'bg-sky-500'
                }`} />
                {thread.classification.state}
              </span>
              <span className="px-3 py-1.5 bg-gray-100 rounded-lg text-xs border border-gray-200">{thread.classification.trajectory}</span>
              <span className="px-3 py-1.5 bg-gray-100 rounded-lg text-xs border border-gray-200">{thread.classification.participation_balance}</span>
              <span className="px-3 py-1.5 bg-gray-100 rounded-lg text-xs border border-gray-200">{thread.classification.discourse_quality}</span>
              <span className="px-3 py-1.5 bg-gray-100 rounded-lg text-xs border border-gray-200">{thread.classification.inquiry_phase}</span>
            </div>

            <div className="mb-4">
              <div className={`inline-block px-4 py-2 rounded-lg shadow-sm ${
                thread.intervention.decision === 'intervene'
                  ? 'bg-gradient-to-r from-green-500 to-green-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}>
                {thread.intervention.decision === 'intervene' ? 'INTERVENE' : 'NO INTERVENTION'}
              </div>
              {thread.intervention.decision === 'intervene' && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="px-3 py-1.5 bg-gradient-to-r from-dashboard-accent to-dashboard-accent-strong text-white rounded-lg text-xs shadow-sm">
                    {thread.intervention.role}
                  </span>
                  <span className="px-3 py-1.5 bg-gray-200 rounded-lg text-xs border border-gray-300">
                    {thread.intervention.technique}
                  </span>
                  {thread.intervention.post_to_thread !== undefined && (
                    <span className="px-3 py-1.5 bg-gray-200 rounded-lg text-xs border border-gray-300">
                      {thread.intervention.post_to_thread ? 'posted' : 'instructor-only'}
                    </span>
                  )}
                </div>
              )}
            </div>

            <div className="grid grid-cols-4 gap-3">
              <div className="relative">
                <div className="text-xs text-gray-500 mb-1.5">Classification</div>
                <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-dashboard-accent to-dashboard-accent-strong opacity-30"
                    style={{ width: `${thread.classification.confidence * 100}%` }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center font-mono text-xs text-gray-900">
                    {thread.classification.confidence.toFixed(2)}
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="text-xs text-gray-500 mb-1.5">Intervention</div>
                <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-dashboard-accent to-dashboard-accent-strong opacity-30"
                    style={{ width: `${thread.intervention.confidence * 100}%` }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center font-mono text-xs text-gray-900">
                    {thread.intervention.confidence.toFixed(2)}
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="text-xs text-gray-500 mb-1.5">Role</div>
                <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-dashboard-accent to-dashboard-accent-strong opacity-30"
                    style={{ width: `${(thread.role_confidence || 0) * 100}%` }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center font-mono text-xs text-gray-900">
                    {thread.role_confidence?.toFixed(2) || '—'}
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="text-xs text-gray-500 mb-1.5">Response</div>
                <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-dashboard-accent to-dashboard-accent-strong opacity-30"
                    style={{ width: `${(thread.response?.confidence || 0) * 100}%` }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center font-mono text-xs text-gray-900">
                    {thread.response?.confidence.toFixed(2) || '—'}
                  </div>
                </div>
              </div>
            </div>

            {isExpanded && (
              <div className="mt-6 pt-6 border-t border-gray-200 space-y-4 text-sm">
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Classification reasoning</div>
                  <div className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">{thread.classification.reasoning}</div>
                </div>

                {thread.intervention.reasoning && (
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Intervention reasoning</div>
                    <div className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">{thread.intervention.reasoning}</div>
                  </div>
                )}

                {thread.role_reasoning && (
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Role reasoning</div>
                    <div className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">{thread.role_reasoning}</div>
                  </div>
                )}

                {thread.response && (
                  <>
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Response reasoning</div>
                      <div className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">{thread.response.reasoning}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Response text</div>
                      <div className="p-4 bg-gradient-to-r from-dashboard-accent/10 to-transparent border-l-4 border-dashboard-accent italic text-gray-800 rounded-r-lg leading-relaxed">
                        "{thread.response.text}"
                      </div>
                    </div>
                  </>
                )}

                {thread.messages && thread.messages.length > 0 && (
                  <div>
                    <button
                      type="button"
                      className="flex items-center gap-1 text-xs text-gray-500 uppercase tracking-wide mb-2 hover:text-gray-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedMessages(
                          expandedMessages === thread.thread_key ? null : thread.thread_key
                        );
                      }}
                    >
                      {expandedMessages === thread.thread_key
                        ? <ChevronDown size={12} />
                        : <ChevronRight size={12} />}
                      Agent messages ({thread.messages.length})
                    </button>
                    {expandedMessages === thread.thread_key && (
                      <pre className="text-xs text-gray-700 bg-gray-50 p-4 rounded-lg border border-gray-200 overflow-x-auto whitespace-pre-wrap break-words max-h-96 overflow-y-auto">
                        {JSON.stringify(thread.messages, null, 2)}
                      </pre>
                    )}
                  </div>
                )}

                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Intervention history</div>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    {historyLoadingByThread[thread.thread_key] && (
                      <div className="text-xs text-gray-500">Loading history...</div>
                    )}
                    {historyErrorsByThread[thread.thread_key] && !historyLoadingByThread[thread.thread_key] && (
                      <div className="space-y-2">
                        <div className="text-xs text-red-600">
                          {historyErrorsByThread[thread.thread_key]}
                        </div>
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            loadHistoryForThread(thread.thread_key, true);
                          }}
                          className="rounded border border-red-200 bg-red-50 px-2 py-1 text-xs text-red-700 hover:bg-red-100"
                        >
                          Retry
                        </button>
                      </div>
                    )}
                    {Object.prototype.hasOwnProperty.call(historyByThread, thread.thread_key)
                      && historyByThread[thread.thread_key].length > 0 ? (
                      <div className="space-y-2">
                        {historyByThread[thread.thread_key]
                          .slice(-3)
                          .reverse()
                          .map((item, idx) => (
                            <div
                              key={`${item.timestamp}-${idx}`}
                              className="rounded border border-gray-200 bg-white px-3 py-2"
                            >
                              <div className="text-xs text-gray-500">
                                {new Date(item.timestamp).toLocaleString()} · {item.role} · {item.technique}
                              </div>
                              <div className="mt-1 text-xs text-gray-700 line-clamp-2">
                                {item.response_text}
                              </div>
                            </div>
                          ))}
                      </div>
                    ) : (
                      !historyLoadingByThread[thread.thread_key]
                      && !historyErrorsByThread[thread.thread_key] && (
                        <div className="text-xs text-gray-500">
                          No recorded interventions for this thread.
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  const interventionTotal = Object.values(model.threads).filter(
    t => !t.error && t.intervention.decision === 'intervene'
  ).length;

  return (
    <div className="p-8 max-w-[1600px] mx-auto">
      <div className="mb-8">
        <div className="mb-3 flex items-center gap-2 text-sm text-gray-500">
          <button
            type="button"
            onClick={onBackToHistory}
            className="rounded-md px-1 py-0.5 text-sm text-gray-700 transition-colors hover:text-gray-900"
          >
            Runs
          </button>
          <span>/</span>
          <button
            type="button"
            onClick={onBackToRunOverview}
            className="rounded-md px-1 py-0.5 text-sm text-gray-700 transition-colors hover:text-gray-900"
          >
            {runName}
          </button>
          <span>/</span>
          <span className="text-gray-900">{model.model_name}</span>
        </div>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-1 h-8 bg-gradient-to-b from-dashboard-accent to-dashboard-accent-strong rounded-full" />
          <div>
            <div className="text-[11px] uppercase tracking-[0.24em] text-gray-500 mb-1">Model detail</div>
            <h1 className="text-3xl text-gray-900 font-mono">{model.model_name}</h1>
            <p className="mt-1 text-sm text-gray-500">Run #{runId} · {runName}</p>
          </div>
        </div>

      <div className="flex gap-6 mb-8 text-sm bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs">Completion:</span>
          <span className="font-mono text-gray-900">{model.completion_count}/{model.total_threads}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs">Classification accuracy:</span>
          <span className="font-mono text-gray-900">
            {hasExpectedState
              ? `${model.classification_correct}/${expectedComparableCount}`
              : 'N/A (classified-only run)'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs">Intervention accuracy:</span>
          <span className="font-mono text-gray-900">
            {interventionTotal > 0 ? `${model.intervention_count} triggered` : '—'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs">Avg duration:</span>
          <span className="font-mono text-gray-900">{model.avg_duration}ms</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs">Errors:</span>
          <span className={`font-mono ${model.error_count > 0 ? 'text-red-600' : 'text-gray-900'}`}>{model.error_count}</span>
        </div>
      </div>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {scenarios.map(renderThreadCard)}
      </div>
    </div>
  );
}
