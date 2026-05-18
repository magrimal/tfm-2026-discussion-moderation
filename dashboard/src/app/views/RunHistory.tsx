import type { ExperimentRun } from '../types';

interface RunHistoryProps {
  runs: ExperimentRun[];
  selectedRunId: string;
  onRunSelect: (runId: string) => void;
}

const statusTone = {
  passed: 'bg-emerald-500',
  unstable: 'bg-amber-500',
  failed: 'bg-rose-500',
  running: 'bg-sky-500',
} as const;

export function RunHistory({ runs, selectedRunId, onRunSelect }: RunHistoryProps) {
  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="mb-6">
        <div className="text-[11px] uppercase tracking-[0.24em] text-gray-500 mb-2">
          Builds
        </div>
        <h1 className="text-3xl text-gray-900">Run history</h1>
        <p className="text-sm text-gray-500 mt-2">
          Recent pipeline runs with status-first inspection.
        </p>
      </div>

      <div className="bg-white border border-gray-300 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b border-gray-300">
            <tr>
              <th className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]">Status</th>
              <th className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]">Run</th>
              <th className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]">Timestamp</th>
              <th className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]">Models</th>
              <th className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]">Failures</th>
              <th className="text-left px-5 py-3 text-gray-600 uppercase tracking-wide text-[11px]">Action</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => {
              const models = Object.values(run.models);
              const failures = models.reduce((sum, model) => sum + model.error_count, 0);
              const isSelected = run.run_id === selectedRunId;

              return (
                <tr
                  key={run.run_id}
                  className={`border-b border-gray-200 ${isSelected ? 'bg-slate-50' : 'bg-white hover:bg-gray-50'}`}
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
                  </td>
                  <td className="px-5 py-4 text-gray-700">
                    {new Date(run.timestamp).toLocaleString()}
                  </td>
                  <td className="px-5 py-4 text-gray-700">{models.length}</td>
                  <td className="px-5 py-4">
                    <span className={`font-mono text-xs px-2 py-1 rounded ${failures > 0 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {failures}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <button
                      onClick={() => onRunSelect(run.run_id)}
                      className="px-3 py-1.5 rounded-md bg-[#31414a] text-white text-xs hover:bg-[#243038] transition-colors"
                    >
                      Open
                    </button>
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