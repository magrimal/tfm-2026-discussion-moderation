import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { RunHistory } from './views/RunHistory';
import { RunDetail } from './views/RunDetail';
import { ModelDetail } from './views/ModelDetail';
import { Trigger } from './views/Trigger';

import { mockHistoricalRuns } from './data/mockData';
import { fetchRunDetail, fetchRunSummaries } from './api';
import type { ExperimentRun, RunSummary } from './types';

export default function App() {
  const [activeSection, setActiveSection] = useState('runs');
  const [runsView, setRunsView] = useState<'history' | 'overview' | 'model'>('history');
  const [runSummaries, setRunSummaries] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState(mockHistoricalRuns[0].run_id);
  const [selectedRun, setSelectedRun] = useState<ExperimentRun>(mockHistoricalRuns[0]);
  const [selectedModelForDetail, setSelectedModelForDetail] = useState<string | null>(null);
  const [isLoadingRuns, setIsLoadingRuns] = useState(true);
  const [runsError, setRunsError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadRuns = async () => {
      try {
        const summaries = await fetchRunSummaries();
        if (!isMounted || summaries.length === 0) {
          return;
        }

        setRunSummaries(summaries);
        setSelectedRunId(summaries[0].run_id);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setRunsError(
          error instanceof Error
            ? `${error.message} Falling back to sample data.`
            : 'Failed to load runs. Falling back to sample data.'
        );
        setRunSummaries(
          mockHistoricalRuns.map((run) => ({
            run_id: run.run_id,
            run_name: run.run_name,
            timestamp: run.timestamp,
            run_kind: run.run_kind,
            status: run.status,
            model_count: Object.keys(run.models).length,
            thread_count: Object.values(run.models)[0]
              ? Object.keys(Object.values(run.models)[0].threads).length
              : 0,
            total_runs: Object.values(run.models).reduce(
              (sum, model) => sum + model.total_threads,
              0
            ),
            completed_runs: Object.values(run.models).reduce(
              (sum, model) => sum + model.completion_count,
              0
            ),
            error_count: Object.values(run.models).reduce(
              (sum, model) => sum + model.error_count,
              0
            ),
            avg_duration_ms: Math.round(
              Object.values(run.models).reduce(
                (sum, model) => sum + model.avg_duration,
                0
              ) / Math.max(Object.keys(run.models).length, 1)
            ),
            summary_available: Boolean(run.summary_markdown),
          }))
        );
      } finally {
        if (isMounted) {
          setIsLoadingRuns(false);
        }
      }
    };

    loadRuns();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    const loadRunDetail = async () => {
      const isMockRun = mockHistoricalRuns.some((run) => run.run_id === selectedRunId);
      if (runsError && isMockRun) {
        const fallbackRun = mockHistoricalRuns.find((run) => run.run_id === selectedRunId);
        if (fallbackRun && isMounted) {
          setSelectedRun(fallbackRun);
        }
        return;
      }

      try {
        const detail = await fetchRunDetail(selectedRunId);
        if (isMounted) {
          setSelectedRun(detail);
        }
      } catch (error) {
        if (!isMounted) {
          return;
        }

        const fallbackRun = mockHistoricalRuns.find((run) => run.run_id === selectedRunId);
        if (fallbackRun) {
          setSelectedRun(fallbackRun);
        }
        setRunsError(
          error instanceof Error
            ? `${error.message} Showing sample data where needed.`
            : 'Failed to load run detail. Showing sample data where needed.'
        );
      }
    };

    loadRunDetail();

    return () => {
      isMounted = false;
    };
  }, [runsError, selectedRunId]);

  const handleRunChange = (runId: string) => {
    setSelectedRunId(runId);
    setSelectedModelForDetail(null);
    setRunsView('overview');
  };

  const handleModelClick = (modelName: string) => {
    setSelectedModelForDetail(modelName);
    setRunsView('model');
  };

  const renderRunsView = () => {
    if (runsView === 'history') {
      return (
        <RunHistory
          runs={runSummaries}
          selectedRunId={selectedRunId}
          onRunSelect={(runId) => {
            handleRunChange(runId);
            setRunsView('overview');
          }}
        />
      );
    }
    if (runsView === 'overview') {
      return (
        <RunDetail
          run={selectedRun}
          onModelSelect={handleModelClick}
          onBackToHistory={() => setRunsView('history')}
        />
      );
    }
    if (runsView === 'model') {
      const model = selectedModelForDetail
        ? selectedRun.models[selectedModelForDetail]
        : Object.values(selectedRun.models)[0];
      return model ? (
        <ModelDetail
          model={model}
          runId={selectedRun.run_id}
          runName={selectedRun.run_name}
          onBackToRunOverview={() => setRunsView('overview')}
          onBackToHistory={() => setRunsView('history')}
        />
      ) : (
        <div className="p-8">No model selected</div>
      );
    }
    return null;
  };

  const renderView = () => {
    if (activeSection === 'runs') {
      return renderRunsView();
    }
    if (activeSection === 'trigger') {
      return (
        <Trigger
          onRunTriggered={() => {
            setActiveSection('runs');
            setRunsView('history');
          }}
        />
      );
    }

    return null;
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-white">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
      />
      <div className="flex-1 overflow-y-auto">
        {runsError && (
          <div className="mx-8 mt-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {runsError}
          </div>
        )}
        {isLoadingRuns && (
          <div className="mx-8 mt-6 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
            Loading runs from the local API...
          </div>
        )}
        {renderView()}
      </div>
    </div>
  );
}