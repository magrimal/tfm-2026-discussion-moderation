import { ExternalLink, CircleHelp } from 'lucide-react';
import type { ExperimentRun } from '../types';
import { Tooltip, TooltipContent, TooltipTrigger } from '../components/ui/tooltip';
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
    passed: 'bg-emerald-500 text-emerald-50',
    unstable: 'bg-amber-500 text-amber-50',
    failed: 'bg-rose-500 text-rose-50',
    running: 'bg-sky-500 text-sky-50',
    noop: 'bg-gray-400 text-gray-50',
  } as const;

  return (
    <div className="p-8 max-w-[1600px] mx-auto bg-[#f8f9fb] min-h-full">
      {/* Header */}
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
          <span className="text-gray-900">{run.run_name}</span>
        </div>
        <div className="bg-[#31414a] text-white rounded-xl px-6 py-5 shadow-sm border border-[#31414a]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-[11px] uppercase tracking-[0.24em] text-slate-300 mb-2">
                Build #{run.run_id}
              </div>
              <h1 className="text-3xl text-white">{run.run_name}</h1>
              <p className="text-sm text-slate-300 mt-1.5">
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
              <div className={`px-3 py-1.5 rounded-md text-xs uppercase tracking-[0.18em] ${statusTone[run.status ?? 'unstable']}`}>
                {run.status ?? 'unstable'}
              </div>
              {run.run_type && (
                <div className={`px-3 py-1.5 rounded-md text-xs uppercase tracking-[0.18em] ${
                  run.run_type === 'live'
                    ? 'bg-violet-500 text-violet-50'
                    : 'bg-slate-600 text-slate-100'
                }`}>
                  {run.run_type}
                </div>
              )}
            </div>
          </div>
          {run.status === 'running' && (
            <div className="mt-4 rounded-lg border border-sky-300/40 bg-sky-500/20 px-4 py-3 text-sm text-sky-50">
              <div className="font-medium">Pipeline running</div>
              <div className="mt-1 text-sky-100">
                {run.progress_message ?? 'Executing stages...'}
              </div>
              {typeof run.completed_runs === 'number' && typeof run.total_runs === 'number' && run.total_runs > 0 && (
                <div className="mt-1 font-mono text-xs text-sky-100">
                  {run.completed_runs}/{run.total_runs} checks completed
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-4 mb-8 lg:grid-cols-[1.4fr_1fr]">
        <div className="bg-white border border-gray-300 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="text-sm uppercase tracking-[0.24em] text-gray-500">Run summary</h2>
              <p className="text-xs text-gray-500 mt-1">
                Plain-language checkpoints for whether this run is healthy enough to inspect further.
              </p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">Coverage</div>
              <div className="text-lg font-semibold text-gray-900">{completedEvaluations} of {totalEvaluations} checks completed</div>
              <p className="text-xs text-gray-600 mt-2">
                This counts all model-by-scenario executions that produced a result.
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">Classification match</div>
              <div className="text-lg font-semibold text-gray-900">
                {classificationAccuracy !== null
                  ? `${classificationAccuracy}% matched the expected scenario`
                  : 'Not applicable for classified-only runs'}
              </div>
              <p className="text-xs text-gray-600 mt-2">
                {classificationAccuracy !== null
                  ? 'This is the main signal used by the trace matrix cell colors.'
                  : 'This run does not include expected states, so the matrix shows classified state only.'}
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">Execution health</div>
              <div className="text-lg font-semibold text-gray-900">{successRate}% finished without recorded execution errors</div>
              <p className="text-xs text-gray-600 mt-2">
                Use this to judge whether the run is broadly reliable before drilling into one model.
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">Timing</div>
              <div className="text-lg font-semibold text-gray-900">{avgDuration}ms average per model</div>
              <p className="text-xs text-gray-600 mt-2">
                {totalErrors > 0 ? `${totalErrors} execution errors were also recorded in this run.` : 'No execution errors were recorded in this run.'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl p-6 shadow-sm">
          <h2 className="text-sm uppercase tracking-[0.24em] text-gray-500 mb-4">What this run contains</h2>
          <div className="space-y-4 text-sm text-gray-700">
            <div className="flex items-start justify-between gap-4">
              <span className="text-gray-500">Models</span>
              <span className="font-medium text-gray-900">{modelCount}</span>
            </div>
            <div className="flex items-start justify-between gap-4">
              <span className="text-gray-500">Scenarios</span>
              <span className="font-medium text-gray-900">{scenarioCount}</span>
            </div>
            <div className="flex items-start justify-between gap-4">
              <span className="text-gray-500">Run status</span>
              <span className="font-medium text-gray-900 capitalize">{run.status ?? 'unstable'}</span>
            </div>
            <div className="pt-4 border-t border-gray-200 text-xs text-gray-500 leading-relaxed">
              Start in the trace matrix if you want to compare models side by side. Open a model name when one row looks suspicious and you need per-thread detail.
            </div>
          </div>
        </div>
      </div>

      {/* Run Scope */}
      <div className="bg-white border border-gray-300 rounded-xl p-6 mb-8 shadow-sm">
        <div className="flex items-center justify-between mb-4 gap-4">
          <div>
            <h3 className="text-sm text-gray-500 uppercase tracking-wide">Run scope</h3>
            <p className="text-xs text-gray-500 mt-1">
              Keep this section to the inputs that define what was executed, not every runtime parameter.
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-600">
            {models.length} models x {scenarios.length} scenarios
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <div className="text-xs text-gray-500 mb-3">Models in this run</div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {models.map((model) => {
                const accuracy = model.completion_count > 0
                  ? Math.round((model.classification_correct / model.completion_count) * 100)
                  : null;
                return (
                  <div
                    key={model.model_name}
                    className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-mono text-sm text-gray-900">{model.model_name}</div>
                        <div className="mt-1 text-xs text-gray-500">
                          {model.completion_count}/{model.total_threads} completed
                          {accuracy !== null && hasExpectedState && (
                            <span className={`ml-2 font-medium ${accuracy >= 70 ? 'text-emerald-600' : accuracy >= 40 ? 'text-amber-600' : 'text-rose-600'}`}>
                              {accuracy}% match
                            </span>
                          )}
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => onModelSelect(model.model_name)}
                        className="rounded-md bg-[#31414a] px-3 py-1.5 text-xs text-white transition-colors hover:bg-[#243038]"
                      >
                        Inspect model
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-500 mb-3">Thread scenarios ({scenarios.length})</div>
            <div className="flex items-center gap-2 flex-wrap">
              {scenarios.map((scenario) => (
                <div
                  key={scenario.key}
                  className="px-3 py-1.5 bg-gray-100 border border-gray-200 rounded-lg text-xs font-mono text-gray-700"
                >
                  {scenario.label}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* LogFuse Access Grid */}
      <div className="bg-white border border-gray-300 rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
          <div className="flex items-center gap-2 mb-1">
            <ExternalLink className="w-4 h-4 text-[#5A9FA8]" />
            <h3 className="text-sm text-gray-900 uppercase tracking-wide">Trace matrix</h3>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="inline-flex h-4 w-4 items-center justify-center rounded-full text-gray-400 transition-colors hover:text-gray-700"
                >
                  <CircleHelp className="h-3.5 w-3.5" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="top" sideOffset={6} className="max-w-64 bg-[#31414a] text-white">
                {hasExpectedState
                  ? 'Use this as the main comparison grid: rows are models, columns are discussion scenarios, and cells show whether each model matched the expected state. Cells only link out when the run recorded a trace URL.'
                  : 'Use this as the main inspection grid: rows are models, columns are thread keys, and cells show the classified state for each execution. Cells link out only when the run recorded a trace URL.'}
              </TooltipContent>
            </Tooltip>
          </div>
          <p className="text-xs text-gray-500">
            {hasExpectedState
              ? 'Cells show execution status for each model-state pair. When a trace URL exists, the cell also links to LogFuse.'
              : 'Cells show execution status for each model-thread pair and display the classified state. When a trace URL exists, the cell also links to LogFuse.'}
          </p>
            <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-3 text-xs text-gray-600">
                <span className="font-medium text-gray-900">Rows</span>: models evaluated in this run.
              </div>
              <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-3 text-xs text-gray-600">
                <span className="font-medium text-gray-900">Columns</span>: {hasExpectedState ? 'expected discussion states found in this run.' : 'thread keys found in this run.'}
              </div>
              <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-3 text-xs text-gray-600">
                <span className="font-medium text-gray-900">Cells</span>: {hasExpectedState ? (<><span className="font-mono text-green-700 bg-green-100 px-1 rounded">✓</span> correct state, classified state name if wrong, <span className="font-mono text-red-700 bg-red-100 px-1 rounded">ERR</span> on error.</>) : (<>classified state name, or <span className="font-mono text-red-700 bg-red-100 px-1 rounded">ERR</span> on error.</>)}
              </div>
            </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-4 text-gray-600 sticky left-0 bg-gray-50 z-10 font-medium">
                  Model
                </th>
                {scenarios.map((scenario) => (
                  <th key={scenario.key} className="px-4 py-4 text-gray-600 min-w-[100px] font-medium">
                      <div className="flex items-center justify-center gap-1.5 text-center font-mono text-xs">
                        <span>{scenario.label}</span>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <button
                              type="button"
                              className="inline-flex h-4 w-4 items-center justify-center rounded-full text-gray-400 transition-colors hover:text-gray-700"
                            >
                              <CircleHelp className="h-3.5 w-3.5" />
                            </button>
                          </TooltipTrigger>
                          <TooltipContent side="top" sideOffset={6} className="max-w-56 bg-[#31414a] text-white">
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
                  className="border-b border-gray-100 hover:bg-gray-50/50 transition-colors"
                >
                  <td className="px-6 py-4 font-mono text-xs sticky left-0 bg-white hover:bg-gray-50/50 z-10 border-r border-gray-100">
                    <button
                      type="button"
                      onClick={() => onModelSelect(model.model_name)}
                      className="flex w-full items-center gap-2 text-left"
                      title="Open model detail"
                    >
                      <div className="w-1.5 h-8 bg-gradient-to-b from-[#5A9FA8] to-[#4A8F98] rounded-full" />
                      <div>
                        <div className="text-gray-900">{model.model_name}</div>
                        <div className="text-[10px] text-gray-500 mt-0.5">
                          {model.completion_count}/{model.total_threads} • {model.avg_duration}ms
                        </div>
                      </div>
                    </button>
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
                      : 'bg-gray-100 text-gray-400';

                    const cellContent = hasError ? (
                      <span className="text-xs font-mono font-semibold">ERR</span>
                    ) : thread ? (
                      hasExpectedForThread && isCorrect ? (
                        <span className="text-xs font-mono font-semibold">✓</span>
                      ) : (
                        <span className="text-[10px] font-mono font-semibold leading-tight text-center px-1">
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
                            <TooltipContent side="top" sideOffset={6} className="max-w-56 bg-[#31414a] text-white">
                              {tooltipText}
                            </TooltipContent>
                          </Tooltip>
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center">
                            <span className="text-gray-400 text-xs">—</span>
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
