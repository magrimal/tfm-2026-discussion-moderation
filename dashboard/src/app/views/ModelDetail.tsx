import { useState } from 'react';
import { ModelResult } from '../types';
import { ChevronDown, ChevronRight, ExternalLink } from 'lucide-react';
import { getScenarioDescriptors } from '../scenarios';
import { WorkflowNote } from '../components/WorkflowNote';

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const totalSeconds = ms / 1000;
  if (totalSeconds < 60) return `${totalSeconds.toFixed(1)}s`;
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.round(totalSeconds % 60);
  return `${minutes}m ${seconds}s`;
}

interface ModelDetailProps {
  model: ModelResult;
  runName: string;
  onBackToRunOverview: () => void;
  onBackToHistory: () => void;
}

export function ModelDetail({
  model,
  runName,
  onBackToRunOverview,
  onBackToHistory,
}: ModelDetailProps) {
  const [expandedThread, setExpandedThread] = useState<string | null>(null);
  const threads = Object.values(model.threads);
  const sourceCourses = Array.from(
    new Set(threads.map((thread) => thread.course_id).filter(Boolean))
  );
  const sourceDetails = sourceCourses.length === 1
    ? {
        label: sourceCourses[0],
        description: 'These discussion threads came from the Open edX course shown here.',
      }
    : {
        label: 'Sample data',
        description: 'These discussion threads are built-in example discussions that come with this project.',
      };

  const scenarios = getScenarioDescriptors(
    threads.map(
      (thread) => thread.expected_state || thread.thread_key
    )
  );

  const renderThreadRow = (scenario: { key: string; label: string }) => {
    const thread = Object.values(model.threads).find(
      (item) => (item.expected_state || item.thread_key) === scenario.key
    );
    if (!thread) return null;

    const isExpanded = expandedThread === scenario.key;

    return (
      <details
        key={scenario.key}
        open={isExpanded}
        onToggle={(e) => setExpandedThread(e.currentTarget.open ? scenario.key : null)}
        className={`border-b border-border last:border-b-0 ${thread.error ? 'border-l-4 border-l-red-600' : ''}`}
      >
        <summary className="flex items-center gap-4 px-5 py-4 cursor-pointer hover:bg-muted/30 transition-colors list-none">
          <div className="flex-shrink-0 text-muted-foreground">
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </div>

          <div className="flex-1 min-w-0">
            <span className="text-sm font-medium text-foreground">{thread.thread_title || scenario.label}</span>
            {thread.thread_body && (
              <p className="mt-1 text-xs text-muted-foreground truncate">
                {thread.thread_body}
              </p>
            )}
            {!thread.error && (
              <div className="mt-1 text-xs text-muted-foreground">
                Prediction: {thread.classification.state} · Suggested action: {thread.intervention.decision === 'intervene' ? 'intervene' : 'no action'}
              </div>
            )}
          </div>

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
        </summary>

        {!thread.error && (
          <div className="px-5 pb-5 pt-3 space-y-4 text-sm border-t border-border bg-muted/20">
            {(thread.thread_body || (thread.thread_comments?.length ?? 0) > 0) && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-1">Discussion</h3>
                <div className="rounded-lg border border-border bg-background p-3 space-y-3">
                  {thread.thread_body && (
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">Opening post</div>
                      <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                        {thread.thread_body}
                      </p>
                    </div>
                  )}
                  {(thread.thread_comments?.length ?? 0) > 0 && (
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">Replies</div>
                      <div className="space-y-2">
                        {thread.thread_comments?.map((comment, index) => (
                          <div
                            key={`${thread.thread_key}-comment-${index}`}
                            className="border-l-2 border-border pl-3"
                          >
                            <div className="text-xs font-medium text-foreground mb-1">
                              {comment.author}
                            </div>
                            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                              {comment.body}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {thread.expected_state && (
              <div className="text-xs text-muted-foreground">
                Reference answer: <span className="font-medium text-foreground">{thread.expected_state}</span>
              </div>
            )}

            <div>
              <h3 className="text-sm font-semibold text-foreground mb-1">Prediction</h3>
              <p className="text-sm text-foreground leading-relaxed">
                The model predicts this thread is <span className="font-medium">{thread.classification.state}</span>.
                <span className="text-muted-foreground"> Confidence {thread.classification.confidence.toFixed(2)}.</span>
              </p>
              <div className="mt-3 rounded-lg border border-border bg-background p-3">
                <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">Why</div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {thread.classification.reasoning}
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-foreground mb-1">Suggested action</h3>
              <p className="text-sm text-foreground leading-relaxed">
                <span className="font-medium">
                  {thread.intervention.decision === 'intervene' ? 'Intervene' : 'No action'}
                </span>
                {thread.intervention.decision === 'intervene' && thread.intervention.role && (
                  <span className="text-muted-foreground"> using {thread.intervention.role}</span>
                )}
              </p>
              {thread.intervention.decision === 'intervene' && thread.intervention.technique && (
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                  Method: {thread.intervention.technique}
                </p>
              )}
              {thread.intervention.reasoning && (
                <div className="mt-3 rounded-lg border border-border bg-background p-3">
                  <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">Why</div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {thread.intervention.reasoning}
                  </p>
                </div>
              )}
            </div>

            {thread.response && (
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-1">Suggested reply</h3>
                <div className="rounded-lg border border-border bg-background p-3 text-sm text-foreground leading-relaxed">
                  {thread.response.text}
                </div>
                {thread.response.reasoning && (
                  <details className="mt-3 rounded-lg border border-border bg-background p-3">
                    <summary className="cursor-pointer list-none text-sm font-medium text-foreground">
                      Why this reply
                    </summary>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                      {thread.response.reasoning}
                    </p>
                  </details>
                )}
              </div>
            )}
          </div>
        )}
      </details>
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
            <h1 className="text-2xl text-foreground font-mono">{model.model_name}</h1>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">Model details</h2>
      </div>

      <div className="mb-8 rounded-xl border border-border bg-background p-5 text-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-muted-foreground text-xs">Source:</span>
          <span className="font-medium text-foreground">{sourceDetails.label}</span>
        </div>
        <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
          {sourceDetails.description}
        </p>
      </div>

      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">Run overview</h2>
      </div>

      <div className="flex flex-wrap gap-6 mb-8 text-sm bg-background border border-border rounded-xl p-5">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Completion:</span>
          <span className="font-mono text-foreground">{model.completion_count}/{model.total_threads}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Suggested actions triggered:</span>
          <span className="font-mono text-foreground">
            {interventionTotal > 0 ? `${model.intervention_count} triggered` : 'N/A'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Errors:</span>
          <span className={`font-mono ${model.error_count > 0 ? 'text-red-600' : 'text-foreground'}`}>{model.error_count}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-xs">Avg. speed:</span>
          <span className="font-mono text-foreground">{formatDuration(model.avg_duration)} / thread</span>
        </div>
      </div>

      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">Threads reviewed</h2>
      </div>

      <WorkflowNote
        title="How to read this page"
        steps={[
          'Open a thread to see the model prediction, suggested action, and draft reply.',
          'Read the short summary first, then open the Why sections if you need the detailed reasoning.',
          'Use the reference answer to compare the model output when one is available.',
        ]}
      />

      <div className="-mt-2 mb-4">
        <p className="text-xs text-muted-foreground">
          Error rows show the failure message instead of a full report.
        </p>
      </div>

      <div className="bg-background border border-border rounded-xl overflow-hidden">
        {scenarios.map(renderThreadRow)}
      </div>
    </div>
  );
}
