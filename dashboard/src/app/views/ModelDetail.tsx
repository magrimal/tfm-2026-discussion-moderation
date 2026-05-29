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

  const renderThreadRow = (scenario: { key: string; label: string }) => {
    const thread = Object.values(model.threads).find(
      (item) => (item.expected_state || item.thread_key) === scenario.key
    );
    if (!thread) return null;

    const isExpanded = expandedThread === scenario.key;

    return (
      <div key={scenario.key} className={`border-b border-border last:border-b-0 ${thread.error ? 'border-l-4 border-l-red-600' : ''}`}>
        <div
          className="flex items-center gap-4 px-5 py-4 cursor-pointer hover:bg-muted/30 transition-colors"
          onClick={() => toggleThread(scenario.key)}
        >
          <div className="flex-shrink-0 text-muted-foreground">
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </div>

          <div className="flex-1 min-w-0">
            <span className="text-sm font-medium text-foreground">{thread.thread_title || scenario.label}</span>
          </div>

          {!thread.error && (
            <div className="flex items-center gap-2 flex-shrink-0 flex-wrap justify-end">
              <span className="inline-flex items-center gap-1.5 px-2 py-1 bg-muted rounded text-xs border border-border">
                <div className={`w-1.5 h-1.5 rounded-full ${
                  thread.expected_state
                    ? (thread.classification.state === thread.expected_state ? 'bg-green-600' : 'bg-yellow-500')
                    : 'bg-sky-500'
                }`} />
                {thread.classification.state}
              </span>
              <span className={`px-2 py-1 rounded text-xs ${
                thread.intervention.decision === 'intervene'
                  ? 'bg-status-passed text-white'
                  : 'bg-muted text-muted-foreground border border-border'
              }`}>
                {thread.intervention.decision === 'intervene' ? 'intervene' : 'no intervention'}
              </span>
            </div>
          )}

          {thread.error && (
            <span className="text-xs text-red-600 flex-shrink-0">{thread.error}</span>
          )}

          {thread.logfuse_url && (
            <a
              href={thread.logfuse_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex-shrink-0 flex items-center gap-1 px-2 py-1 text-xs bg-dashboard-accent text-white rounded hover:bg-dashboard-accent-strong transition-colors"
            >
              LogFuse
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>

        {isExpanded && !thread.error && (
          <div className="px-5 pb-5 pt-3 space-y-4 text-sm border-t border-border bg-muted/20">
            {thread.expected_state && (
              <div className="text-xs font-mono text-muted-foreground">
                Expected state: <span className="text-foreground">{thread.expected_state}</span>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              <span className="px-2 py-1 bg-muted rounded text-xs border border-border"><span className="text-muted-foreground">trajectory:</span> {thread.classification.trajectory}</span>
              <span className="px-2 py-1 bg-muted rounded text-xs border border-border"><span className="text-muted-foreground">balance:</span> {thread.classification.participation_balance}</span>
              <span className="px-2 py-1 bg-muted rounded text-xs border border-border"><span className="text-muted-foreground">discourse:</span> {thread.classification.discourse_quality}</span>
              <span className="px-2 py-1 bg-muted rounded text-xs border border-border"><span className="text-muted-foreground">phase:</span> {thread.classification.inquiry_phase}</span>
            </div>

            {thread.intervention.decision === 'intervene' && (
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-dashboard-accent text-white rounded text-xs">{thread.intervention.role}</span>
                <span className="px-2 py-1 bg-muted rounded text-xs border border-border">{thread.intervention.technique}</span>
                {thread.intervention.post_to_thread !== undefined && (
                  <span className="px-2 py-1 bg-muted rounded text-xs border border-border">
                    {thread.intervention.post_to_thread ? 'posted' : 'instructor-only'}
                  </span>
                )}
              </div>
            )}

            <div className="flex gap-6 text-xs text-muted-foreground">
              <span>Classification <span className="font-mono text-foreground ml-1">{thread.classification.confidence.toFixed(2)}</span></span>
              <span>Intervention <span className="font-mono text-foreground ml-1">{thread.intervention.confidence.toFixed(2)}</span></span>
              <span>Role <span className="font-mono text-foreground ml-1">{thread.role_confidence?.toFixed(2) ?? '—'}</span></span>
              <span>Response <span className="font-mono text-foreground ml-1">{thread.response?.confidence.toFixed(2) ?? '—'}</span></span>
            </div>

            {(() => {
              const stages = thread.pipeline_messages
                ? Object.entries(thread.pipeline_messages)
                : thread.messages && thread.messages.length > 0
                  ? [['role', thread.messages] as [string, object[]]]
                  : [];
              return stages.length > 0 ? (
                <div className="space-y-2">
                  <div className="text-xs text-muted-foreground uppercase tracking-wide">Agent messages</div>
                  {stages.map(([stage, msgs]) => {
                    const stageKey = `${thread.thread_key}:${stage}`;
                    return (
                      <div key={stageKey}>
                        <button
                          type="button"
                          className="flex items-center gap-1 text-xs text-muted-foreground mb-1 hover:text-foreground"
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedMessages(
                              expandedMessages === stageKey ? null : stageKey
                            );
                          }}
                        >
                          {expandedMessages === stageKey
                            ? <ChevronDown size={12} />
                            : <ChevronRight size={12} />}
                          {stage} ({msgs.length})
                        </button>
                        {expandedMessages === stageKey && (
                          <pre className="text-xs text-muted-foreground bg-muted p-4 rounded-lg border border-border overflow-x-auto whitespace-pre-wrap break-words max-h-96 overflow-y-auto">
                            {JSON.stringify(msgs, null, 2)}
                          </pre>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : null;
            })()}

            <div>
              <div className="text-xs text-muted-foreground uppercase tracking-wide mb-2">Classification reasoning</div>
              <div className="text-muted-foreground leading-relaxed bg-muted p-4 rounded-lg text-xs">{thread.classification.reasoning}</div>
            </div>

            {thread.intervention.reasoning && (
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wide mb-2">Intervention reasoning</div>
                <div className="text-muted-foreground leading-relaxed bg-muted p-4 rounded-lg text-xs">{thread.intervention.reasoning}</div>
              </div>
            )}

            {thread.role_reasoning && (
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wide mb-2">Role reasoning</div>
                <div className="text-muted-foreground leading-relaxed bg-muted p-4 rounded-lg text-xs">{thread.role_reasoning}</div>
              </div>
            )}

            {thread.response && (
              <>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wide mb-2">Response reasoning</div>
                  <div className="text-muted-foreground leading-relaxed bg-muted p-4 rounded-lg text-xs">{thread.response.reasoning}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wide mb-2">Response text</div>
                  <div className="p-4 border-l-4 border-dashboard-accent italic text-foreground leading-relaxed text-xs">
                    "{thread.response.text}"
                  </div>
                </div>
              </>
            )}

            <div>
              <div className="text-xs text-muted-foreground uppercase tracking-wide mb-2">Intervention history</div>
              <div className="bg-muted p-4 rounded-lg border border-border">
                {historyLoadingByThread[thread.thread_key] && (
                  <div className="text-xs text-muted-foreground">Loading history...</div>
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
                          className="rounded border border-border bg-background px-3 py-2"
                        >
                          <div className="text-xs text-muted-foreground">
                            {new Date(item.timestamp).toLocaleString()} · {item.role} · {item.technique}
                          </div>
                          <div className="mt-1 text-xs text-muted-foreground line-clamp-2">
                            {item.response_text}
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  !historyLoadingByThread[thread.thread_key]
                  && !historyErrorsByThread[thread.thread_key] && (
                    <div className="text-xs text-muted-foreground">
                      No recorded interventions for this thread.
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
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
        <div className="mb-3 flex items-center gap-2 text-sm text-muted-foreground">
          <button
            type="button"
            onClick={onBackToHistory}
            className="rounded-md px-1 py-0.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Runs
          </button>
          <span>/</span>
          <button
            type="button"
            onClick={onBackToRunOverview}
            className="rounded-md px-1 py-0.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {runName}
          </button>
          <span>/</span>
          <span className="text-foreground">{model.model_name}</span>
        </div>
        <div className="flex items-center gap-3 mb-4">
          <div>
            <div className="text-caption uppercase tracking-ui text-muted-foreground mb-1">Model detail</div>
            <h1 className="text-3xl text-foreground font-mono">{model.model_name}</h1>
            <p className="mt-1 text-sm text-muted-foreground">Build #{runId} · {runName}</p>
            <p className="mt-0.5 text-xs text-muted-foreground">Each row is a discussion thread. Expand a row to see classification reasoning, intervention decision, and response output.</p>
          </div>
        </div>

      <div className="flex gap-6 mb-8 text-sm bg-background border border-border rounded-xl p-5">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Completion:</span>
          <span className="font-mono text-foreground">{model.completion_count}/{model.total_threads}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Classification accuracy:</span>
          <span className="font-mono text-foreground">
            {hasExpectedState
              ? `${model.classification_correct}/${expectedComparableCount}`
              : 'N/A (classified-only run)'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Intervention accuracy:</span>
          <span className="font-mono text-foreground">
            {interventionTotal > 0 ? `${model.intervention_count} triggered` : '—'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Avg duration:</span>
          <span className="font-mono text-foreground">{model.avg_duration}ms</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Errors:</span>
          <span className={`font-mono ${model.error_count > 0 ? 'text-red-600' : 'text-foreground'}`}>{model.error_count}</span>
        </div>
      </div>
      </div>

      <div className="bg-background border border-border rounded-xl overflow-hidden">
        {scenarios.map(renderThreadRow)}
      </div>
    </div>
  );
}
