import { ExternalLink, CircleHelp } from 'lucide-react';
import type { ExperimentRun } from '../types';
import { Tooltip, TooltipContent, TooltipTrigger } from '../components/Tooltip';
import { getScenarioDescriptors } from '../scenarios';

interface RunDetailProps {
  run: ExperimentRun;
  onModelSelect: (modelName: string) => void;
  onBackToHistory: () => void;
}

export function RunDetail({
  run,
  onModelSelect,
  onBackToHistory,
}: RunDetailProps) {
  const models = Object.values(run.models);
  const expectedComparableCount = models.reduce(
    (sum, model) =>
      sum + Object.values(model.threads).filter(
        (thread) => !thread.error && Boolean(thread.expected_state)
      ).length,
    0
  );
  const hasExpectedState = expectedComparableCount > 0;
  const scenarios = getScenarioDescriptors(
    models.flatMap((model) =>
      Object.values(model.threads).map(
        (thread) => thread.expected_state || thread.thread_key
      )
    )
  );
  const totalEvaluations = models.length * scenarios.length;
  const completedEvaluations = models.reduce((sum, m) => sum + m.completion_count, 0);
  const totalModelThreads = models.reduce((sum, m) => sum + m.total_threads, 0);
  const successRate = totalModelThreads > 0
    ? Math.round(
      (models.reduce((sum, m) => sum + (m.total_threads - m.error_count), 0) /
        totalModelThreads) * 100
    )
    : 0;
  const avgDuration = models.length > 0
    ? Math.round(models.reduce((sum, m) => sum + m.avg_duration, 0) / models.length)
    : 0;
  const classificationAccuracy = hasExpectedState
    ? Math.round(
      (models.reduce((sum, m) => sum + m.classification_correct, 0) /
        expectedComparableCount) * 100
    )
    : null;
  const totalErrors = models.reduce((sum, m) => sum + m.error_count, 0);
  const scenarioCount = scenarios.length;
  const modelCount = models.length;

  const statusTone = {
    passed: 'bg-status-passed-bg text-status-passed border border-status-passed-border',
    unstable: 'bg-status-unstable-bg text-status-unstable border border-status-unstable-border',
    failed: 'bg-status-failed-bg text-status-failed border border-status-failed-border',
    running: 'bg-status-running-bg text-status-running border border-status-running-border',
    noop: 'bg-status-noop-bg text-status-noop border border-status-noop-border',
  } as const;

  return (
    <div className="p-8 max-w-[1600px] mx-auto bg-muted min-h-full">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-3 flex items-center gap-2 text-sm text-muted-foreground">
          <button
            type="button"
            onClick={onBackToHistory}
            className="rounded px-1 py-0.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Runs
          </button>
          <span>/</span>
          <span className="text-foreground">{run.run_name}</span>
        </div>
        <div className="rounded-xl border border-border bg-background px-6 py-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-caption uppercase tracking-ui text-muted-foreground mb-2">
                Build #{run.run_id}
              </div>
              <h1 className="text-3xl text-foreground">{run.run_name}</h1>
              <p className="text-sm text-muted-foreground mt-1.5">
                {new Date(run.timestamp).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className={`px-3 py-1 rounded text-xs uppercase tracking-ui-sm ${statusTone[run.status ?? 'unstable']}`}>
                {run.status ?? 'unstable'}
              </div>
              {run.run_type && (
                <div className={`px-3 py-1 rounded text-xs uppercase tracking-ui-sm border ${
                  run.run_type === 'live'
                    ? 'bg-violet-50 text-violet-700 border-violet-200'
                    : 'bg-muted text-muted-foreground border-border'
                }`}>
                  {run.run_type}
                </div>
              )}
            </div>
          </div>
          {run.status === 'running' && (
            <div className="mt-4 rounded border border-status-running-border bg-status-running-bg px-4 py-3 text-sm text-status-running">
              <div className="font-medium">Pipeline running</div>
              <div className="mt-1">
                {run.progress_message ?? 'Executing stages...'}
              </div>
              {typeof run.completed_runs === 'number' && typeof run.total_runs === 'number' && run.total_runs > 0 && (
                <div className="mt-1 font-mono text-xs">
                  {run.completed_runs}/{run.total_runs} checks completed
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="bg-background border border-border rounded-xl overflow-hidden mb-8">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-caption uppercase tracking-ui text-muted-foreground">Run summary</h2>
        </div>
        <div className="divide-y divide-border">
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Models</span>
            <span className="font-mono text-foreground">{modelCount}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Scenarios</span>
            <span className="font-mono text-foreground">{scenarioCount}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Coverage</span>
            <span className="font-mono text-foreground">{completedEvaluations}/{totalEvaluations} checks completed</span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Classification match</span>
            <span className="font-mono text-foreground">
              {classificationAccuracy !== null ? `${classificationAccuracy}%` : 'N/A'}
            </span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Execution health</span>
            <span className="font-mono text-foreground">{successRate}% without errors</span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Avg duration</span>
            <span className="font-mono text-foreground">{avgDuration}ms per model</span>
          </div>
          {totalErrors > 0 && (
            <div className="flex items-center justify-between px-5 py-3 text-sm">
              <span className="text-muted-foreground">Execution errors</span>
              <span className="font-mono text-red-600">{totalErrors}</span>
            </div>
          )}
        </div>
      </div>

      {/* Trace matrix */}
      <div className="bg-background border border-border rounded-xl overflow-hidden">
        <div className="p-6 border-b border-border bg-background">
          <div className="flex items-center gap-2 mb-1">
            <ExternalLink className="w-4 h-4 text-dashboard-accent" />
            <h3 className="text-sm text-foreground uppercase tracking-wide">Trace matrix</h3>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="inline-flex h-4 w-4 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
                >
                  <CircleHelp className="h-3.5 w-3.5" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="top" sideOffset={6} className="max-w-64 bg-dashboard-panel text-white">
                {hasExpectedState
                  ? 'Use this as the main comparison grid: rows are models, columns are discussion scenarios, and cells show whether each model matched the expected state. Cells only link out when the run recorded a trace URL.'
                  : 'Use this as the main inspection grid: rows are models, columns are thread keys, and cells show the classified state for each execution. Cells link out only when the run recorded a trace URL.'}
              </TooltipContent>
            </Tooltip>
          </div>
          <p className="text-xs text-muted-foreground">
            {hasExpectedState
              ? 'Cells show execution status for each model-state pair. When a trace URL exists, the cell also links to LogFuse.'
              : 'Cells show execution status for each model-thread pair and display the classified state. When a trace URL exists, the cell also links to LogFuse.'}
          </p>
            <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-lg border border-border bg-muted px-3 py-3 text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Rows</span>: models evaluated in this run.
              </div>
              <div className="rounded-lg border border-border bg-muted px-3 py-3 text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Columns</span>: {hasExpectedState ? 'expected discussion states found in this run.' : 'thread keys found in this run.'}
              </div>
              <div className="rounded-lg border border-border bg-muted px-3 py-3 text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Cells</span>: {hasExpectedState ? (<><span className="font-mono text-green-700 bg-green-100 px-1 rounded">✓</span> correct state, classified state name if wrong, <span className="font-mono text-red-700 bg-red-100 px-1 rounded">ERR</span> on error.</>) : (<>classified state name, or <span className="font-mono text-red-700 bg-red-100 px-1 rounded">ERR</span> on error.</>)}
              </div>
            </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted border-b border-border">
              <tr>
                <th className="text-left px-6 py-4 text-muted-foreground sticky left-0 bg-muted z-10 font-medium">
                  Model
                </th>
                {scenarios.map((scenario) => (
                  <th key={scenario.key} className="px-4 py-4 text-muted-foreground min-w-[100px] font-medium">
                      <div className="flex items-center justify-center gap-1.5 text-center font-mono text-xs">
                        <span>{scenario.label}</span>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <button
                              type="button"
                              className="inline-flex h-4 w-4 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground"
                            >
                              <CircleHelp className="h-3.5 w-3.5" />
                            </button>
                          </TooltipTrigger>
                          <TooltipContent side="top" sideOffset={6} className="max-w-56 bg-dashboard-panel text-white">
                            {hasExpectedState
                              ? `${scenario.description} Expected state for this scenario: ${scenario.key}. A green cell means the model predicted this state correctly.`
                              : `Thread key ${scenario.key}. Cells show the model classification output for executions in this thread.`}
                          </TooltipContent>
                        </Tooltip>
                      </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {models.map((model) => (
                <tr
                  key={model.model_name}
                  className="border-b border-border hover:bg-muted/50 transition-colors"
                >
                  <td className="px-6 py-4 font-mono text-xs sticky left-0 bg-background hover:bg-muted/50 z-10 border-r border-border">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-foreground">{model.model_name}</div>
                        <div className="text-label text-muted-foreground mt-0.5">
                          {model.completion_count}/{model.total_threads} • {model.avg_duration}ms
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => onModelSelect(model.model_name)}
                        className="flex-shrink-0 text-xs text-dashboard-accent hover:underline"
                      >
                        View details
                      </button>
                    </div>
                  </td>
                  {scenarios.map((scenario) => {
                    const thread = Object.values(model.threads).find(
                      (item) => (item.expected_state || item.thread_key) === scenario.key
                    );
                    const hasError = thread?.error;
                    const logfuseUrl = thread?.logfuse_url;
                    const hasExpectedForThread = Boolean(thread?.expected_state);
                    const isCorrect = Boolean(
                      thread
                      && !hasError
                      && hasExpectedForThread
                      && thread.classification.state === thread.expected_state
                    );
                    const cellClasses = hasError
                      ? 'bg-red-100 text-red-600'
                      : thread
                      ? hasExpectedForThread
                        ? isCorrect
                          ? 'bg-green-100 text-green-600'
                          : 'bg-yellow-100 text-yellow-700'
                        : 'bg-sky-100 text-sky-700'
                      : 'bg-muted text-muted-foreground';

                    const cellContent = hasError ? (
                      <span className="text-xs font-mono font-semibold">ERR</span>
                    ) : thread ? (
                      hasExpectedForThread && isCorrect ? (
                        <span className="text-xs font-mono font-semibold">✓</span>
                      ) : (
                        <span className="text-label font-mono font-semibold leading-tight text-center px-1">
                          {thread.classification.state ?? '?'}
                        </span>
                      )
                    ) : (
                      <span className="text-xs">—</span>
                    );

                    const tooltipText = !thread
                      ? `No result was recorded for ${model.model_name} in ${scenario.key}.`
                      : hasError
                      ? `Execution error for ${model.model_name} on ${scenario.key}.${logfuseUrl ? ' Open the trace for failure details.' : ' This run did not record a trace URL.'}`
                      : hasExpectedForThread && isCorrect
                      ? `${model.model_name} matched the expected ${scenario.key} state.${logfuseUrl ? ' Open the trace for the full reasoning.' : ' This run did not record a trace URL.'}`
                      : hasExpectedForThread
                      ? `${model.model_name} ran for ${scenario.key} but classified it as ${thread.classification.state}.${logfuseUrl ? ' Open the trace to inspect the mismatch.' : ' This run did not record a trace URL.'}`
                      : `${model.model_name} classified thread ${scenario.key} as ${thread.classification.state}.${logfuseUrl ? ' Open the trace to inspect full reasoning.' : ' This run did not record a trace URL.'}`;

                    return (
                      <td key={scenario.key} className="px-4 py-4 text-center">
                        {thread ? (
                          <Tooltip>
                            <TooltipTrigger asChild>
                              {logfuseUrl ? (
                                <a
                                  href={logfuseUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="group relative inline-block"
                                >
                                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center transition-all group-hover:shadow-md ${cellClasses}`}>
                                    {cellContent}
                                  </div>
                                </a>
                              ) : (
                                <div className={`inline-flex w-12 h-12 rounded-lg items-center justify-center ${cellClasses}`}>
                                  {cellContent}
                                </div>
                              )}
                            </TooltipTrigger>
                            <TooltipContent side="top" sideOffset={6} className="max-w-56 bg-dashboard-panel text-white">
                              {tooltipText}
                            </TooltipContent>
                          </Tooltip>
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center">
                            <span className="text-muted-foreground text-xs">—</span>
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
