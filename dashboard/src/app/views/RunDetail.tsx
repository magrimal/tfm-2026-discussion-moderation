import type { ExperimentRun } from '../types';

interface RunDetailProps {
  run: ExperimentRun;
  onModelSelect: (modelName: string) => void;
  onBackToHistory: () => void;
  onCancelRun?: (runId: string) => void;
}

export function RunDetail({
  run,
  onModelSelect,
  onBackToHistory,
  onCancelRun,
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

  const totalEvaluations = models.reduce(
    (sum, model) => sum + model.total_threads,
    0
  );
  const completedEvaluations = models.reduce((sum, m) => sum + m.completion_count, 0);
  const totalErrors = models.reduce((sum, m) => sum + m.error_count, 0);
  const modelCount = models.length;

  const getModelComparableCount = (model: (typeof models)[number]) => (
    Object.values(model.threads).filter(
      (thread) => !thread.error && Boolean(thread.expected_state)
    ).length
  );

  const getModelCoverageRatio = (model: (typeof models)[number]) => (
    model.total_threads > 0
      ? model.completion_count / model.total_threads
      : 0
  );

  const getModelMatchRatio = (model: (typeof models)[number]) => {
    const comparable = getModelComparableCount(model);
    if (comparable === 0) {
      return -1;
    }
    return model.classification_correct / comparable;
  };

  const listModels = [...models].sort((left, right) => {
    if (right.error_count !== left.error_count) {
      return right.error_count - left.error_count;
    }
    const coverageDiff = getModelCoverageRatio(left) - getModelCoverageRatio(right);
    if (coverageDiff !== 0) {
      return coverageDiff;
    }
    return getModelMatchRatio(left) - getModelMatchRatio(right);
  });

  return (
    <div className="p-8 max-w-[1600px] mx-auto bg-muted min-h-full">
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
          <div>
            <h1 className="text-3xl text-foreground">{run.run_name}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Run #{run.run_id} ·
              {new Date(run.timestamp).toLocaleString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
          {run.status === 'running' && (
            <div className="mt-4 rounded border border-status-running-border bg-status-running-bg px-4 py-3 text-sm text-status-running">
              <div className="flex items-center justify-between">
                <div className="font-medium">Run in progress</div>
                {onCancelRun && (
                  <button
                    type="button"
                    onClick={() => onCancelRun(run.run_id)}
                    className="ml-4 rounded px-3 py-1 text-xs font-medium border border-status-running text-status-running hover:bg-status-running hover:text-white transition-colors"
                  >
                    Cancel
                  </button>
                )}
              </div>
              <div className="mt-1">
                {run.progress_message ?? 'Working through the steps...'}
              </div>
              {typeof run.completed_runs === 'number' && typeof run.total_runs === 'number' && run.total_runs > 0 && (
                <div className="mt-1 font-mono text-xs">
                  {run.completed_runs}/{run.total_runs} comparisons completed
                </div>
              )}
            </div>
          )}
          {run.status === 'cancelling' && (
            <div className="mt-4 rounded border border-status-unstable-border bg-status-unstable-bg px-4 py-3 text-sm text-status-unstable">
              <div className="font-medium">Cancelling...</div>
              <div className="mt-1">
                Waiting for the current step to finish.
              </div>
            </div>
          )}
          {run.status === 'cancelled' && (
            <div className="mt-4 rounded border border-border bg-muted px-4 py-3 text-sm text-muted-foreground">
              <div className="font-medium">Run cancelled</div>
              <div className="mt-1">
                The run was stopped early. Partial results are shown below.
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="bg-background border border-border rounded-xl overflow-hidden mb-8">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Run summary</h2>
          <p className="text-xs text-muted-foreground mt-1">
            This is a quick overview of the whole run before you open a model.
          </p>
        </div>
        <div className="divide-y divide-border">
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Models</span>
            <span className="font-mono text-foreground">{modelCount}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Completed evaluations</span>
            <span className="font-mono text-foreground">{completedEvaluations} of {totalEvaluations}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-3 text-sm">
            <span className="text-muted-foreground">Errors</span>
            <span className={`font-mono ${totalErrors > 0 ? 'text-red-600' : 'text-foreground'}`}>{totalErrors}</span>
          </div>
        </div>
      </div>

      <div className="bg-background border border-border rounded-xl overflow-hidden">
        <div className="p-6 border-b border-border bg-background">
          <h2 className="text-lg font-semibold text-foreground">Model comparison</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Use this view to compare models, then open one for the full thread view.
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Sorted by errors, then completion rate, then correct predictions.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted border-b border-border">
              <tr>
                <th className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption">Model</th>
                <th className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption">Completed</th>
                <th className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption">Correct predictions</th>
                <th className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption">Errors</th>
                <th className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption">Details</th>
              </tr>
            </thead>
            <tbody>
              {listModels.map((model) => (
                <tr key={model.model_name} className="border-b border-border">
                  <td className="px-5 py-4 font-mono text-xs text-foreground">{model.model_name}</td>
                  <td className="px-5 py-4 text-xs text-muted-foreground">
                    {model.completion_count}/{model.total_threads}
                  </td>
                  <td className="px-5 py-4 text-xs text-muted-foreground">
                    {(() => {
                      const comparable = getModelComparableCount(model);
                      if (!hasExpectedState || comparable === 0) {
                        return 'N/A';
                      }
                      return `${model.classification_correct}/${comparable}`;
                    })()}
                  </td>
                  <td className="px-5 py-4">
                    <span className={`font-mono text-xs px-2 py-1 rounded ${model.error_count > 0 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {model.error_count}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <button
                      type="button"
                      onClick={() => onModelSelect(model.model_name)}
                      className="text-xs text-dashboard-accent hover:underline"
                    >
                      View details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
