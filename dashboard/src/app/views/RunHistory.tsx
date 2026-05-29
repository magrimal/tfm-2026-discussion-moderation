import { useState } from 'react';
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
  passed: 'bg-status-passed',
  unstable: 'bg-status-unstable',
  failed: 'bg-status-failed',
  running: 'bg-status-running',
  noop: 'bg-status-noop',
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
  const [hoveredRunId, setHoveredRunId] = useState<string | null>(null);

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="text-caption uppercase tracking-ui text-muted-foreground mb-2">
            Builds
          </div>
          <h1 className="text-3xl text-foreground">Build history</h1>
          <p className="text-sm text-muted-foreground mt-2">
            Select a build to inspect its trace matrix and per-model results.
          </p>
        </div>
        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            title="Reload runs"
            className="mt-1 p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="bg-background border border-border rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-muted border-b border-border">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.label}
                  className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption"
                >
                  <div className="inline-flex items-center gap-1.5">
                    <span>{column.label}</span>
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

              const isHovered = hoveredRunId === run.run_id;
              const cellCls = `transition-colors ${isSelected || isHovered ? 'bg-muted' : ''}`;

              return (
                <tr
                  key={run.run_id}
                  onClick={() => onRunSelect(run.run_id)}
                  onMouseEnter={() => setHoveredRunId(run.run_id)}
                  onMouseLeave={() => setHoveredRunId(null)}
                  className="cursor-pointer border-b border-border"
                >
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <div className="inline-flex items-center gap-2 uppercase tracking-wide text-caption text-muted-foreground">
                      {run.status && (
                        <span className={`h-2.5 w-2.5 rounded-full ${statusTone[run.status]}`} />
                      )}
                      {run.status ?? 'unknown'}
                    </div>
                  </td>
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <div className="font-medium text-foreground">{run.run_name}</div>
                    <div className="font-mono text-xs text-muted-foreground mt-1">{run.run_id}</div>
                    {run.run_type && (
                      <span className={`inline-block mt-1.5 px-2 py-0.5 rounded text-label uppercase tracking-wide font-medium ${
                        run.run_type === 'live'
                          ? 'bg-violet-100 text-violet-700'
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {run.run_type}
                      </span>
                    )}
                  </td>
                  <td className={`px-5 py-4 text-muted-foreground ${cellCls}`}>
                    {new Date(run.timestamp).toLocaleString('es-ES', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    })}
                  </td>
                  <td className={`px-5 py-4 text-muted-foreground ${cellCls}`}>{run.model_count}</td>
                  <td className={`px-5 py-4 text-muted-foreground ${cellCls}`}>{run.thread_count}</td>
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <span className="font-mono text-xs text-muted-foreground">
                      {run.completed_runs}/{run.total_runs}
                    </span>
                  </td>
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <span className="text-xs text-muted-foreground">
                      {run.progress_message ?? (run.status === 'running' ? 'Running...' : 'Completed')}
                    </span>
                  </td>
                  <td className={`px-5 py-4 ${cellCls}`}>
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
