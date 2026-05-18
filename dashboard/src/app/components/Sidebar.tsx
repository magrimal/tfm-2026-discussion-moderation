interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  selectedRunId: string;
  onRunChange: (runId: string) => void;
  availableRuns: Array<{ run_id: string; run_name: string; status?: string }>;
  selectedModels: string[];
  onModelToggle: (model: string) => void;
  availableModels: string[];
  tierFilter: string[];
  onTierFilterChange: (tiers: string[]) => void;
}

export function Sidebar({
  activeView,
  onViewChange,
  selectedRunId,
  onRunChange,
  availableRuns,
  selectedModels,
  onModelToggle,
  availableModels,
  tierFilter,
  onTierFilterChange
}: SidebarProps) {
  const views = [
    { id: 'history', label: 'Run history' },
    { id: 'run-detail', label: 'Run overview' },
    { id: 'heatmap', label: 'Heatmap' },
    { id: 'model-detail', label: 'Model detail' },
    { id: 'trigger', label: 'Trigger run' },
    { id: 'configuration', label: 'Configuration' }
  ];

  const tiers = ['Full', 'Partial', 'None'];

  const toggleTier = (tier: string) => {
    if (tierFilter.includes(tier)) {
      onTierFilterChange(tierFilter.filter(t => t !== tier));
    } else {
      onTierFilterChange([...tierFilter, tier]);
    }
  };

  const selectedRun =
    availableRuns.find((run) => run.run_id === selectedRunId) ??
    availableRuns[0];

  const statusTone = {
    passed: 'bg-emerald-500',
    unstable: 'bg-amber-500',
    failed: 'bg-rose-500',
    running: 'bg-sky-500',
  } as const;

  return (
    <div className="w-72 bg-[#f3f4f6] border-r border-gray-300 h-screen flex flex-col p-5 shadow-sm">
      <div className="mb-6 border-b border-gray-300 pb-5">
        <div className="text-[10px] uppercase tracking-[0.24em] text-gray-500 mb-2">
          discussion_moderation
        </div>
        <h1 className="text-lg text-gray-900 mb-1">Dashboard</h1>
        <div className="text-xs text-gray-500">Runs, traces, and pipeline checks</div>
      </div>

      <div className="mb-5 rounded-lg border border-gray-300 bg-white p-3">
        <div className="flex items-center justify-between mb-3">
          <label className="text-[10px] text-gray-500 uppercase tracking-[0.2em] block">Selected run</label>
          {selectedRun?.status && (
            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-gray-600">
              <span className={`h-2 w-2 rounded-full ${statusTone[selectedRun.status as keyof typeof statusTone]}`} />
              {selectedRun.status}
            </span>
          )}
        </div>
        <select
          value={selectedRunId}
          onChange={(event) => onRunChange(event.target.value)}
          className="w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#5A9FA8] focus:border-transparent transition-all"
        >
          {availableRuns.map((run) => (
            <option key={run.run_id} value={run.run_id}>
              {run.run_name}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-5">
        <label className="text-[10px] text-gray-500 uppercase tracking-[0.2em] block mb-3">Views</label>
        <div className="space-y-1.5">
          {views.map(view => (
            <button
              key={view.id}
              onClick={() => onViewChange(view.id)}
              className={`w-full text-left px-3 py-2.5 text-sm rounded-md transition-all border ${
                activeView === view.id
                  ? 'bg-[#31414a] border-[#31414a] text-white shadow-sm'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-100'
              }`}
            >
              {view.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-5 rounded-lg border border-gray-300 bg-white p-3">
        <label className="text-[10px] text-gray-500 uppercase tracking-[0.2em] block mb-3">Models</label>
        <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
          {availableModels.map(model => (
            <label key={model} className="flex items-center text-sm cursor-pointer group">
              <input
                type="checkbox"
                checked={selectedModels.includes(model)}
                onChange={() => onModelToggle(model)}
                className="mr-3 w-4 h-4 rounded border-gray-300 text-[#5A9FA8] focus:ring-[#5A9FA8]"
              />
              <span className="font-mono text-xs text-gray-800 group-hover:text-[#5A9FA8] transition-colors">{model}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="mt-auto rounded-lg border border-gray-300 bg-white p-3">
        <label className="text-[10px] text-gray-500 uppercase tracking-[0.2em] block mb-3">Tier Filter</label>
        <div className="flex gap-2">
          {tiers.map(tier => (
            <button
              key={tier}
              onClick={() => toggleTier(tier)}
              className={`flex-1 px-2 py-2 text-xs rounded-lg transition-all ${
                tierFilter.includes(tier)
                  ? 'bg-[#31414a] text-white shadow-sm'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
