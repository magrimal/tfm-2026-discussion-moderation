import { useEffect, useMemo, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { RunHistory } from './views/RunHistory';
import { RunDetail } from './views/RunDetail';
import { ModelDetail } from './views/ModelDetail';
import { Trigger } from './views/Trigger';

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

const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');
const toPath = (path: string) => `${BASE}${path}`;

function parseDashboardPath(pathname: string): DashboardRoute {
  const stripped = pathname.startsWith(BASE) ? pathname.slice(BASE.length) : pathname;
  const normalized = stripped.replace(/\/+$/, '') || '/';
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
  runId: string | null,
  modelName: string | null,
): string {
  if (!runId) {
    return toPath('/runs');
  }
  if (runsView === 'history') {
    return toPath('/runs');
  }
  if (runsView === 'overview') {
    return toPath(`/runs/${encodeURIComponent(runId)}`);
  }
  if (!modelName) {
    return toPath(`/runs/${encodeURIComponent(runId)}`);
  }
  return toPath(
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
  const [selectedRunId, setSelectedRunId] = useState<string | null>(
    initialRoute.runId
  );
  const [selectedRun, setSelectedRun] = useState<ExperimentRun | null>(null);
  const [selectedModelForDetail, setSelectedModelForDetail] = useState<string | null>(
    initialRoute.modelName
  );
  const [isLoadingRuns, setIsLoadingRuns] = useState(true);
  const [runsError, setRunsError] = useState<string | null>(null);

  const refreshRuns = async () => {
    try {
      const summaries = await fetchRunSummaries();
      setRunSummaries(summaries);
      const selectedExists = selectedRunId
        ? summaries.some((run) => run.run_id === selectedRunId)
        : false;
      if (!selectedExists) {
        setSelectedRunId(null);
      }
      setRunsError(null);
    } catch (error) {
      setRunsError(error instanceof Error ? error.message : 'Failed to load runs.');
    }
  };

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

        setRunSummaries(summaries);
        const selectedExists = selectedRunId
          ? summaries.some((run) => run.run_id === selectedRunId)
          : false;
        if (!selectedExists) {
          setSelectedRunId(null);
        }
        setRunsError(null);
        if (summaries.length > 0) {
          setIsLoadingRuns(false);
        }
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setRunsError(
          error instanceof Error ? error.message : 'Failed to load runs.'
        );
        setRunSummaries([]);
        setSelectedRunId(null);
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
    if (!selectedRunId) {
      setSelectedRun(null);
      return () => {
        isMounted = false;
      };
    }

    const loadRunDetail = async () => {
      try {
        const detail = await fetchRunDetail(selectedRunId);
        if (isMounted) {
          setSelectedRun(detail);
          setRunsError(null);
        }
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setSelectedRun(null);
        setRunsError(
          error instanceof Error
            ? error.message
            : 'Failed to load selected run detail.'
        );
      }
    };

    loadRunDetail();

    return () => {
      isMounted = false;
    };
  }, [selectedRunId]);

  useEffect(() => {
    if (activeSection === 'trigger') {
      if (window.location.pathname !== toPath('/trigger')) {
        navigateToPath(toPath('/trigger'), true);
      }
      return;
    }

    const targetPath = buildRunsPath(
      runsView,
      selectedRunId,
      selectedModelForDetail,
    );
    if (window.location.pathname !== targetPath) {
      navigateToPath(targetPath, true);
    }
  }, [activeSection, runsView, selectedModelForDetail, selectedRunId]);

  const handleRunChange = (runId: string) => {
    navigateToPath(toPath(`/runs/${encodeURIComponent(runId)}`));
  };

  const handleModelClick = (modelName: string) => {
    if (!selectedRunId) {
      return;
    }
    navigateToPath(toPath(
      `/runs/${encodeURIComponent(selectedRunId)}`
      + `/model-details/${encodeURIComponent(modelName)}`
    ));
  };

  const renderRunsView = () => {
    if (runsView === 'history') {
      return (
        <RunHistory
          runs={runSummaries}
          onRunSelect={(runId) => {
            handleRunChange(runId);
          }}
          onRefresh={refreshRuns}
        />
      );
    }
    if (runsView === 'overview') {
      if (!selectedRun) {
        return <div className="p-8 text-sm text-gray-600">No run selected.</div>;
      }
      return (
        <RunDetail
          run={selectedRun}
          onModelSelect={handleModelClick}
          onBackToHistory={() => navigateToPath(toPath('/runs'))}
        />
      );
    }
    if (runsView === 'model') {
      if (!selectedRun) {
        return <div className="p-8 text-sm text-gray-600">No run selected.</div>;
      }
      const model = selectedModelForDetail
        ? selectedRun.models[selectedModelForDetail]
        : Object.values(selectedRun.models)[0];
      return model ? (
        <ModelDetail
          model={model}
          runId={selectedRun.run_id}
          runName={selectedRun.run_name}
          onBackToRunOverview={() => {
            navigateToPath(toPath(`/runs/${encodeURIComponent(selectedRunId)}`));
          }}
          onBackToHistory={() => navigateToPath(toPath('/runs'))}
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
            refreshRuns().catch(() => {});
            navigateToPath(toPath('/runs'));
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
          navigateToPath(section === 'trigger' ? toPath('/trigger') : toPath('/runs'));
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