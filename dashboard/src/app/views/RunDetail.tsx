import { ExternalLink, Activity, CheckCircle2, XCircle, Clock, TrendingUp, GitBranch, Layers3, Bot } from 'lucide-react';
import { ExperimentRun } from '../types';
import { threadScenarios } from '../data/mockData';

interface RunDetailProps {
  run: ExperimentRun;
}

export function RunDetail({ run }: RunDetailProps) {
  const models = Object.values(run.models);
  const totalEvaluations = models.length * threadScenarios.length;
  const completedEvaluations = models.reduce((sum, m) => sum + m.completion_count, 0);
  const successRate = Math.round(
    (models.reduce((sum, m) => sum + (m.total_threads - m.error_count), 0) /
      models.reduce((sum, m) => sum + m.total_threads, 0)) *
      100
  );
  const avgDuration = Math.round(models.reduce((sum, m) => sum + m.avg_duration, 0) / models.length);
  const classificationAccuracy = Math.round(
    (models.reduce((sum, m) => sum + m.classification_correct, 0) /
      models.reduce((sum, m) => sum + m.completion_count, 0)) *
      100
  );
  const totalErrors = models.reduce((sum, m) => sum + m.error_count, 0);
  const stageData = [
    { label: 'queue', value: 100, icon: GitBranch },
    { label: 'classify', value: classificationAccuracy, icon: Layers3 },
    { label: 'intervene', value: successRate, icon: Bot },
    { label: 'publish', value: totalErrors === 0 ? 100 : Math.max(25, 100 - totalErrors * 15), icon: CheckCircle2 },
  ];

  const statusTone = {
    passed: 'bg-emerald-500 text-emerald-50',
    unstable: 'bg-amber-500 text-amber-50',
    failed: 'bg-rose-500 text-rose-50',
    running: 'bg-sky-500 text-sky-50',
  } as const;

  return (
    <div className="p-8 max-w-[1600px] mx-auto bg-[#f8f9fb] min-h-full">
      {/* Header */}
      <div className="mb-8">
        <div className="bg-[#31414a] text-white rounded-xl px-6 py-5 shadow-sm border border-[#31414a]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-[11px] uppercase tracking-[0.24em] text-slate-300 mb-2">
                Build #{run.run_id}
              </div>
              <h1 className="text-3xl text-white">{run.run_name}</h1>
              <p className="text-sm text-slate-300 mt-1.5">
                {new Date(run.timestamp).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
            <div className={`px-3 py-1.5 rounded-md text-xs uppercase tracking-[0.18em] ${statusTone[run.status ?? 'unstable']}`}>
              {run.status ?? 'unstable'}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-300 rounded-xl p-5 mb-8 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm uppercase tracking-[0.24em] text-gray-500">Stage timeline</h2>
          <div className="text-xs text-gray-500">Status-first execution overview</div>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {stageData.map((stage) => {
            const Icon = stage.icon;
            return (
              <div key={stage.label} className="rounded-lg border border-gray-200 p-4 bg-gray-50">
                <div className="flex items-center justify-between mb-3">
                  <div className="inline-flex items-center gap-2 text-sm font-medium text-gray-800 capitalize">
                    <Icon className="w-4 h-4 text-[#31414a]" />
                    {stage.label}
                  </div>
                  <div className="font-mono text-xs text-gray-500">{stage.value}%</div>
                </div>
                <div className="h-2 rounded-full bg-gray-200 overflow-hidden">
                  <div className="h-full bg-[#31414a]" style={{ width: `${stage.value}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white border border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            </div>
            <div className={`text-xs px-2 py-1 rounded-full ${
              successRate >= 90 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            }`}>
              {successRate >= 90 ? 'Healthy' : 'Attention'}
            </div>
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">{successRate}%</div>
          <div className="text-xs text-gray-500">Success Rate</div>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-xs text-gray-500">{completedEvaluations}/{totalEvaluations}</div>
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">{completedEvaluations}</div>
          <div className="text-xs text-gray-500">Completed Checks</div>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">{classificationAccuracy}%</div>
          <div className="text-xs text-gray-500">Classification Accuracy</div>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="w-5 h-5 text-orange-600" />
            </div>
            {totalErrors > 0 && (
              <div className="flex items-center gap-1 text-xs text-red-600">
                <XCircle className="w-3 h-3" />
                {totalErrors} errors
              </div>
            )}
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">{avgDuration}ms</div>
          <div className="text-xs text-gray-500">Avg Duration</div>
        </div>
      </div>

      {/* Pipeline Configuration */}
      <div className="bg-white border border-gray-300 rounded-xl p-6 mb-8 shadow-sm">
        <h3 className="text-sm text-gray-500 mb-4 uppercase tracking-wide">Run specification</h3>

        <div className="space-y-4">
          <div>
            <div className="text-xs text-gray-500 mb-3">Models</div>
            <div className="flex items-center gap-3 flex-wrap">
              {models.map((model, idx) => (
                <div key={model.model_name} className="flex items-center gap-2">
                  <div className="flex items-center gap-2 px-4 py-2.5 bg-[#31414a] text-white rounded-lg shadow-sm">
                    <div className="w-2 h-2 bg-white rounded-full" />
                    <span className="font-mono text-sm">{model.model_name}</span>
                    <div className="ml-2 px-2 py-0.5 bg-white/20 rounded text-xs">
                      {model.completion_count}/{model.total_threads}
                    </div>
                  </div>
                  {idx < models.length - 1 && (
                    <div className="w-6 h-0.5 bg-gray-300" />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-500 mb-3">Thread Scenarios ({threadScenarios.length})</div>
            <div className="flex items-center gap-2 flex-wrap">
              {threadScenarios.map(scenario => (
                <div
                  key={scenario.key}
                  className="px-3 py-1.5 bg-gray-100 border border-gray-200 rounded-lg text-xs font-mono text-gray-700"
                >
                  {scenario.key}
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div className="flex items-center gap-3">
              <div className="text-xs text-gray-500">Temperature:</div>
              <div className="font-mono text-sm text-gray-900">0.3</div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-xs text-gray-500">Max tokens:</div>
              <div className="font-mono text-sm text-gray-900">4096</div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-xs text-gray-500">LogFuse:</div>
              <div className="font-mono text-xs text-gray-600">logfuse.io/api/v1</div>
            </div>
          </div>
        </div>
      </div>

      {/* LogFuse Access Grid */}
      <div className="bg-white border border-gray-300 rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
          <div className="flex items-center gap-2 mb-1">
            <ExternalLink className="w-4 h-4 text-[#5A9FA8]" />
            <h3 className="text-sm text-gray-900 uppercase tracking-wide">Trace matrix</h3>
          </div>
          <p className="text-xs text-gray-500">
            Click any cell to view detailed execution trace in LogFuse
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-4 text-gray-600 sticky left-0 bg-gray-50 z-10 font-medium">
                  Model
                </th>
                {threadScenarios.map(scenario => (
                  <th key={scenario.key} className="px-4 py-4 text-gray-600 min-w-[100px] font-medium">
                    <div className="text-center font-mono text-xs">{scenario.key}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {models.map((model, idx) => (
                <tr
                  key={model.model_name}
                  className="border-b border-gray-100 hover:bg-gray-50/50 transition-colors"
                >
                  <td className="px-6 py-4 font-mono text-xs sticky left-0 bg-white hover:bg-gray-50/50 z-10 border-r border-gray-100">
                    <div className="flex items-center gap-2">
                      <div className="w-1.5 h-8 bg-gradient-to-b from-[#5A9FA8] to-[#4A8F98] rounded-full" />
                      <div>
                        <div className="text-gray-900">{model.model_name}</div>
                        <div className="text-[10px] text-gray-500 mt-0.5">
                          {model.completion_count}/{model.total_threads} • {model.avg_duration}ms
                        </div>
                      </div>
                    </div>
                  </td>
                  {threadScenarios.map(scenario => {
                    const thread = model.threads[scenario.key];
                    const hasError = thread?.error;
                    const logfuseUrl = thread?.logfuse_url;
                    const isCorrect = thread && !hasError && thread.classification.state === scenario.key;

                    return (
                      <td key={scenario.key} className="px-4 py-4 text-center">
                        {logfuseUrl ? (
                          <a
                            href={logfuseUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group relative inline-block"
                          >
                            <div className={`w-12 h-12 rounded-lg flex items-center justify-center transition-all ${
                              hasError
                                ? 'bg-red-100 group-hover:bg-red-200 group-hover:shadow-md'
                                : isCorrect
                                ? 'bg-green-100 group-hover:bg-green-200 group-hover:shadow-md'
                                : 'bg-yellow-100 group-hover:bg-yellow-200 group-hover:shadow-md'
                            }`}>
                              {hasError ? (
                                <XCircle className="w-5 h-5 text-red-600" />
                              ) : (
                                <ExternalLink className={`w-4 h-4 ${
                                  isCorrect ? 'text-green-600' : 'text-yellow-600'
                                } group-hover:scale-110 transition-transform`} />
                              )}
                            </div>
                          </a>
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center">
                            <span className="text-gray-400 text-xs">—</span>
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
