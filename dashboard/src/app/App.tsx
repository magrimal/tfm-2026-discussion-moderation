import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { RunHistory } from './views/RunHistory';
import { RunDetail } from './views/RunDetail';
import { Heatmap } from './views/Heatmap';
import { ModelDetail } from './views/ModelDetail';
import { Trigger } from './views/Trigger';
import { Configuration } from './views/Configuration';
import { mockHistoricalRuns } from './data/mockData';
import type { ModelResult } from './types';

export default function App() {
  const [activeView, setActiveView] = useState('run-detail');
  const [selectedRunId, setSelectedRunId] = useState(mockHistoricalRuns[0].run_id);
  const selectedRun =
    mockHistoricalRuns.find((run) => run.run_id === selectedRunId) ??
    mockHistoricalRuns[0];
  const [selectedModels, setSelectedModels] = useState<string[]>(
    Object.keys(selectedRun.models)
  );
  const [tierFilter, setTierFilter] = useState<string[]>(['Full', 'Partial', 'None']);
  const [selectedModelForDetail, setSelectedModelForDetail] = useState<string | null>(null);

  const availableModels = Object.keys(selectedRun.models);

  const handleRunChange = (runId: string) => {
    const nextRun = mockHistoricalRuns.find((run) => run.run_id === runId);
    if (!nextRun) {
      return;
    }

    setSelectedRunId(runId);
    setSelectedModels(Object.keys(nextRun.models));
    setSelectedModelForDetail(null);
  };

  const handleModelToggle = (model: string) => {
    if (selectedModels.includes(model)) {
      setSelectedModels(selectedModels.filter(m => m !== model));
    } else {
      setSelectedModels([...selectedModels, model]);
    }
  };

  const filteredModels: ModelResult[] = Object.values(selectedRun.models).filter(model =>
    selectedModels.includes(model.model_name)
  );

  const handleModelClick = (modelName: string) => {
    setSelectedModelForDetail(modelName);
    setActiveView('model-detail');
  };

  const renderView = () => {
    if (activeView === 'history') {
      return (
        <RunHistory
          runs={mockHistoricalRuns}
          selectedRunId={selectedRunId}
          onRunSelect={(runId) => {
            handleRunChange(runId);
            setActiveView('run-detail');
          }}
        />
      );
    }
    if (activeView === 'run-detail') {
      return <RunDetail run={selectedRun} />;
    }
    if (activeView === 'heatmap') {
      return <Heatmap models={filteredModels} />;
    }
    if (activeView === 'model-detail') {
      const model = selectedModelForDetail
        ? selectedRun.models[selectedModelForDetail]
        : filteredModels[0];
      return model ? <ModelDetail model={model} /> : <div className="p-8">No model selected</div>;
    }
    if (activeView === 'trigger') {
      return <Trigger />;
    }
    if (activeView === 'configuration') {
      return <Configuration />;
    }
    return null;
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-white">
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        selectedRunId={selectedRunId}
        onRunChange={handleRunChange}
        availableRuns={mockHistoricalRuns}
        selectedModels={selectedModels}
        onModelToggle={handleModelToggle}
        availableModels={availableModels}
        tierFilter={tierFilter}
        onTierFilterChange={setTierFilter}
      />
      <div className="flex-1 overflow-y-auto">
        {renderView()}
      </div>
    </div>
  );
}