import { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import type { RunSummary } from '../types';

interface RunHistoryProps {
  runs: RunSummary[];
  onRunSelect: (runId: string) => void;
  onRefresh?: () => void;
}

const columns = [
  { label: 'Run' },
  { label: 'Timestamp' },
  { label: 'Completed' },
  { label: 'Progress' },
];

export function RunHistory({ runs, onRunSelect, onRefresh }: RunHistoryProps) {
  const [hoveredRunId, setHoveredRunId] = useState<string | null>(null);

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="text-caption uppercase tracking-ui text-muted-foreground mb-2">
            Runs
          </div>
          <h1 className="text-3xl text-foreground">Run history</h1>
          <p className="text-sm text-muted-foreground mt-2">
            Choose a run to see how each model performed.
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
        <div className="px-5 py-4 border-b border-border bg-background">
          <h2 className="text-lg font-semibold text-foreground">Runs list</h2>
          <p className="text-xs text-muted-foreground">
            Each row is one run. Select a row to open the details.
          </p>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-muted border-b border-border">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.label}
                  className="text-left px-5 py-3 text-muted-foreground uppercase tracking-wide text-caption"
                >
                  <span>{column.label}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => {
              const isHovered = hoveredRunId === run.run_id;
              const cellCls = `transition-colors ${isHovered ? 'bg-muted' : ''}`;

              return (
                <tr
                  key={run.run_id}
                  onClick={() => onRunSelect(run.run_id)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      onRunSelect(run.run_id);
                    }
                  }}
                  onMouseEnter={() => setHoveredRunId(run.run_id)}
                  onMouseLeave={() => setHoveredRunId(null)}
                  className="cursor-pointer border-b border-border"
                  role="button"
                  tabIndex={0}
                  aria-label={`Open run ${run.run_name}`}
                >
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <div className="font-medium text-foreground">{run.run_name}</div>
                  </td>
                  <td className={`px-5 py-4 text-muted-foreground ${cellCls}`}>
                    {new Date(run.timestamp).toLocaleString('en-US', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    })}
                  </td>
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <span className="font-mono text-xs text-muted-foreground">
                      {run.completed_runs} of {run.total_runs}
                    </span>
                  </td>
                  <td className={`px-5 py-4 ${cellCls}`}>
                    <span className="text-xs text-muted-foreground">
                      {run.progress_message ?? (
                        run.status === 'running' ? 'Running...'
                        : run.status === 'cancelling' ? 'Cancelling...'
                        : run.status === 'cancelled' ? 'Cancelled'
                        : 'Finished'
                      )}
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
