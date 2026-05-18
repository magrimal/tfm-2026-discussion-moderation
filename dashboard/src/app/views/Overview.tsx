import { ModelResult } from '../types';
import { ExternalLink } from 'lucide-react';

interface OverviewProps {
  models: ModelResult[];
  onModelClick: (modelName: string) => void;
}

export function Overview({ models, onModelClick }: OverviewProps) {
  const sortedModels = [...models].sort((a, b) => {
    if (b.completion_count !== a.completion_count) {
      return b.completion_count - a.completion_count;
    }
    return b.classification_correct - a.classification_correct;
  });

  return (
    <div className="p-8">
      <h2 className="text-2xl mb-6 text-gray-900">Overview</h2>

      <div className="bg-white border border-gray-300 rounded overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-300">
            <tr>
              <th className="text-left px-4 py-3 text-gray-600">Model name</th>
              <th className="text-left px-4 py-3 text-gray-600">Family</th>
              <th className="text-left px-4 py-3 text-gray-600">Size</th>
              <th className="text-left px-4 py-3 text-gray-600">Completion</th>
              <th className="text-left px-4 py-3 text-gray-600">Classification accuracy</th>
              <th className="text-left px-4 py-3 text-gray-600">Intervene accuracy</th>
              <th className="text-left px-4 py-3 text-gray-600">Avg duration</th>
              <th className="text-left px-4 py-3 text-gray-600">Errors</th>
            </tr>
          </thead>
          <tbody>
            {sortedModels.map((model, idx) => {
              const completionRatio = `${model.completion_count}/${model.total_threads}`;
              const isFullCompletion = model.completion_count === model.total_threads;
              const classificationRatio = `${model.classification_correct}/${model.completion_count}`;

              const interventionTotal = Object.values(model.threads).filter(
                t => !t.error && t.intervention.decision === 'intervene'
              ).length;
              const interventionRatio = interventionTotal > 0 ? `${model.intervention_correct}/${interventionTotal}` : '—';

              return (
                <tr
                  key={model.model_name}
                  onClick={() => onModelClick(model.model_name)}
                  className={`border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'
                  }`}
                >
                  <td className="px-4 py-3 font-mono text-xs text-gray-900">{model.model_name}</td>
                  <td className="px-4 py-3 text-gray-700">{model.family}</td>
                  <td className="px-4 py-3 text-gray-700">{model.size}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        isFullCompletion ? 'bg-[#27AE60]' :
                        model.completion_count >= model.total_threads * 0.8 ? 'bg-yellow-500' :
                        'bg-[#C0392B]'
                      }`} />
                      <span className="font-mono text-xs">{completionRatio}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{classificationRatio}</td>
                  <td className="px-4 py-3 font-mono text-xs">{interventionRatio}</td>
                  <td className="px-4 py-3 font-mono text-xs">{model.avg_duration}ms</td>
                  <td className="px-4 py-3">
                    {model.error_count > 0 && (
                      <span className="inline-block px-2 py-0.5 bg-[#C0392B] text-white text-xs rounded">
                        {model.error_count}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-gray-600">
        Classification accuracy = state matches expected thread label.
        Intervention accuracy = decision matches expected for thread type.
        Click a row to see detailed results or use LogFuse links for execution traces.
      </p>
    </div>
  );
}
