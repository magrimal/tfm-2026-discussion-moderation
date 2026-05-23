import { CircleHelp, RefreshCw } from 'lucide-react';
import type { RunSummary } from '../types';
import { Tooltip, TooltipContent, TooltipTrigger } from '../components/Tooltip';

interface RunHistoryProps {
  runs: RunSummary[];
  selectedRunId: string | null;
  onRunSelect: (runId: string) => void;
  onRefresh?: () => void;
}

const statusTone = {
  passed: 'bg-emerald-500',
  unstable: 'bg-amber-500',
  failed: 'bg-rose-500',
  running: 'bg-sky-500',
  noop: 'bg-gray-400',
} as const;

const columns = [
  {
    label: 'Status',
    tooltip: 'Overall outcome of the run. Running means still active, unstable means mixed results, failed means blocking errors were recorded.',
  },
  {
    label: 'Run',
    tooltip: 'Human-readable run label plus the internal run identifier used to fetch that execution later.',
  },
  {
    label: 'Timestamp',
    tooltip: 'When this run was recorded, shown in your local timezone for quick recency checks.',
  },
  {
    label: 'Models',
    tooltip: 'How many models were included in this run.',
  },
  {
    label: 'Threads',
    tooltip: 'Number of threads evaluated in this run.',
  },
  {
    label: 'Completed',
    tooltip: 'Completed evaluations out of total expected (models × threads). A ratio below 100% means some model-thread pairs did not finish.',
  },
  {
    label: 'Pipeline progress',
    tooltip: 'Live stage feedback for running runs. Shows the current model/thread pair when available.',
  },
  {
    label: 'Failures',
    tooltip: 'Total model-level execution errors across the run. This is not the same as classification mismatch.',
  },
];

export function RunHistory({ runs, selectedRunId, onRunSelect, onRefresh }: RunHistoryProps) {
  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="text-[11px] uppercase tracking-[0.24em] text-gray-500 mb-2">
            Builds
          </div>
          <h1 className="text-3xl text-gray-900">Run history</h1>
          <p className="text-sm text-gray-500 mt-2">
            Recent pipeline runs with status-first inspection.
          </p>
        </div>
        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            title="Reload runs"
            className="mt-1 p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="bg-white border border-gray-300 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b border-gray-300">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.label}
                  className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]"
                >
                  <div className="inline-flex items-center gap-1.5">
                    <span>{column.label}</span>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          type="button"
                          className="inline-flex h-4 w-4 items-center justify-center rounded-full text-gray-400 transition-colors hover:text-gray-700"
                        >
                          <CircleHelp className="h-3.5 w-3.5" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" sideOffset={6} className="max-w-56 bg-dashboard-panel text-white">
                        {column.tooltip}
                      </TooltipContent>
                    </Tooltip>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => {
              const isSelected = run.run_id === selectedRunId;

              return (
                <tr
                  key={run.run_id}
                  onClick={() => onRunSelect(run.run_id)}
                  className={`cursor-pointer border-b border-gray-200 transition-colors ${isSelected ? 'bg-slate-50' : 'bg-white hover:bg-gray-50'}`}
                >
                  <td className="px-5 py-4">
                    <div className="inline-flex items-center gap-2 uppercase tracking-wide text-[11px] text-gray-700">
                      {run.status && (
                        <span className={`h-2.5 w-2.5 rounded-full ${statusTone[run.status]}`} />
                      )}
                      {run.status ?? 'unknown'}
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-medium text-gray-900">{run.run_name}</div>
                    <div className="font-mono text-xs text-gray-500 mt-1">{run.run_id}</div>
                    {run.run_type && (
                      <span className={`inline-block mt-1.5 px-2 py-0.5 rounded text-[10px] uppercase tracking-wide font-medium ${
                        run.run_type === 'live'
                          ? 'bg-violet-100 text-violet-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {run.run_type}
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-gray-700">
                    {new Date(run.timestamp).toLocaleString()}
                  </td>
                  <td className="px-5 py-4 text-gray-700">{run.model_count}</td>
                  <td className="px-5 py-4 text-gray-700">{run.thread_count}</td>
                  <td className="px-5 py-4">
                    <span className="font-mono text-xs text-gray-700">
                      {run.completed_runs}/{run.total_runs}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span className="text-xs text-gray-700">
                      {run.progress_message ?? (run.status === 'running' ? 'Running...' : 'Completed')}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`font-mono text-xs px-2 py-1 rounded ${run.error_count > 0 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {run.error_count}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}