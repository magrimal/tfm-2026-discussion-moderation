import { useEffect, useMemo, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { RunHistory } from './views/RunHistory';
import { RunDetail } from './views/RunDetail';
import { ModelDetail } from './views/ModelDetail';
import { Trigger } from './views/Trigger';

import { mockHistoricalRuns } from './data/mockData';
import { fetchRunDetail, fetchRunSummaries } from './api';
import type { ExperimentRun, RunSummary } from './types';

type DashboardSection = 'runs' | 'trigger';
type RunsView = 'history' | 'overview' | 'model';

interface DashboardRoute {
  section: DashboardSection;
  runsView: RunsView;
  runId: string | null;
  modelName: string | null;
}

function parseDashboardPath(pathname: string): DashboardRoute {
  const normalized = pathname.replace(/\/+$/, '') || '/';
  const parts = normalized.split('/').filter(Boolean);

  if (parts[0] === 'trigger') {
    return {
      section: 'trigger',
      runsView: 'history',
      runId: null,
      modelName: null,
    };
  }

  if (parts[0] === 'runs') {
    if (parts.length >= 4 && parts[2] === 'model-details') {
      return {
        section: 'runs',
        runsView: 'model',
        runId: decodeURIComponent(parts[1]),
        modelName: decodeURIComponent(parts[3]),
      };
    }
    if (parts.length >= 2) {
      return {
        section: 'runs',
        runsView: 'overview',
        runId: decodeURIComponent(parts[1]),
        modelName: null,
      };
    }
  }

  return {
    section: 'runs',
    runsView: 'history',
    runId: null,
    modelName: null,
  };
}

function buildRunsPath(
  runsView: RunsView,
  runId: string,
  modelName: string | null,
): string {
  if (runsView === 'history') {
    return '/runs';
  }
  if (runsView === 'overview') {
    return `/runs/${encodeURIComponent(runId)}`;
  }
  if (!modelName) {
    return `/runs/${encodeURIComponent(runId)}`;
  }
  return (
    `/runs/${encodeURIComponent(runId)}`
    + `/model-details/${encodeURIComponent(modelName)}`
  );
}

export default function App() {
  const initialRoute = useMemo(
    () => parseDashboardPath(window.location.pathname),
    []
  );
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [activeSection, setActiveSection] = useState<DashboardSection>(
    initialRoute.section
  );
  const [runsView, setRunsView] = useState<RunsView>(initialRoute.runsView);
  const [runSummaries, setRunSummaries] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState(
    initialRoute.runId ?? mockHistoricalRuns[0].run_id
  );
  const [selectedRun, setSelectedRun] = useState<ExperimentRun>(
    mockHistoricalRuns.find((run) => run.run_id === initialRoute.runId)
      ?? mockHistoricalRuns[0]
  );
  const [selectedModelForDetail, setSelectedModelForDetail] = useState<string | null>(
    initialRoute.modelName
  );
  const [isLoadingRuns, setIsLoadingRuns] = useState(true);
  const [runsError, setRunsError] = useState<string | null>(null);

  const navigateToPath = (path: string, replace = false) => {
    if (window.location.pathname === path) {
      return;
    }
    if (replace) {
      window.history.replaceState({}, '', path);
    } else {
      window.history.pushState({}, '', path);
    }
    setCurrentPath(path);
  };

  useEffect(() => {
    const onPopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', onPopState);
    return () => {
      window.removeEventListener('popstate', onPopState);
    };
  }, []);

  useEffect(() => {
    const route = parseDashboardPath(currentPath);
    setActiveSection(route.section);
    if (route.section === 'trigger') {
      return;
    }
    setRunsView(route.runsView);
    if (route.runId) {
      setSelectedRunId(route.runId);
    }
    setSelectedModelForDetail(route.modelName);
  }, [currentPath]);

  useEffect(() => {
    let isMounted = true;

    const loadRuns = async () => {
      try {
        const summaries = await fetchRunSummaries();
        if (!isMounted) {
          return;
        }

        if (summaries.length > 0) {
          setRunSummaries(summaries);
          const selectedExists = summaries.some((run) => run.run_id === selectedRunId);
          if (!selectedExists) {
            setSelectedRunId(summaries[0].run_id);
          }
          setRunsError(null);
        }
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
            progress_message: run.progress_message,
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

  useEffect(() => {
    if (activeSection === 'trigger') {
      if (currentPath !== '/trigger') {
        navigateToPath('/trigger', true);
      }
      return;
    }

    const targetPath = buildRunsPath(
      runsView,
      selectedRunId,
      selectedModelForDetail,
    );
    if (targetPath !== currentPath) {
      navigateToPath(targetPath, true);
    }
  }, [
    activeSection,
    currentPath,
    runsView,
    selectedModelForDetail,
    selectedRunId,
  ]);

  const handleRunChange = (runId: string) => {
    navigateToPath(`/runs/${encodeURIComponent(runId)}`);
  };

  const handleModelClick = (modelName: string) => {
    navigateToPath(
      `/runs/${encodeURIComponent(selectedRunId)}`
      + `/model-details/${encodeURIComponent(modelName)}`
    );
  };

  const renderRunsView = () => {
    if (runsView === 'history') {
      return (
        <RunHistory
          runs={runSummaries}
          selectedRunId={selectedRunId}
          onRunSelect={(runId) => {
            handleRunChange(runId);
          }}
        />
      );
    }
    if (runsView === 'overview') {
      return (
        <RunDetail
          run={selectedRun}
          onModelSelect={handleModelClick}
          onBackToHistory={() => navigateToPath('/runs')}
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
          onBackToRunOverview={() => {
            navigateToPath(`/runs/${encodeURIComponent(selectedRunId)}`);
          }}
          onBackToHistory={() => navigateToPath('/runs')}
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
            navigateToPath('/runs');
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
        onSectionChange={(section) => {
          navigateToPath(section === 'trigger' ? '/trigger' : '/runs');
        }}
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