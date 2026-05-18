import { useState } from 'react';
import { ModelResult } from '../types';
import { threadScenarios } from '../data/mockData';

interface HeatmapProps {
  models: ModelResult[];
}

export function Heatmap({ models }: HeatmapProps) {
  const [hoveredCell, setHoveredCell] = useState<{ model: string; thread: string } | null>(null);

  const getCellColor = (modelName: string, threadKey: string, expectedState: string) => {
    const model = models.find(m => m.model_name === modelName);
    if (!model) return 'bg-gray-200';

    const thread = model.threads[threadKey];
    if (!thread) return 'bg-gray-200';
    if (thread.error) return 'bg-gray-300';

    const classifiedState = thread.classification.state;
    if (classifiedState === expectedState) return 'bg-[#27AE60]';

    // Adjacent states (simplified logic)
    const adjacentPairs = [
      ['new', 'stalled'],
      ['active', 'convergent'],
      ['stalled', 'off_topic']
    ];
    const isAdjacent = adjacentPairs.some(
      pair => (pair[0] === classifiedState && pair[1] === expectedState) ||
              (pair[1] === classifiedState && pair[0] === expectedState)
    );

    if (isAdjacent) return 'bg-yellow-200';
    return 'bg-[#C0392B]/70';
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="w-1 h-8 bg-gradient-to-b from-[#5A9FA8] to-[#4A8F98] rounded-full" />
          <h1 className="text-3xl text-gray-900">Classification Heatmap</h1>
        </div>
        <p className="text-sm text-gray-500 mt-2 ml-7">
          Visual comparison of classification results across models and thread scenarios
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gradient-to-r from-gray-50 to-white border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-4 text-gray-600 sticky left-0 bg-gray-50 z-10 font-medium">Model</th>
              {threadScenarios.map(scenario => (
                <th key={scenario.key} className="px-4 py-4 text-gray-600 min-w-[140px] font-medium">
                  <div className="text-center">
                    <div className="font-mono text-xs mb-1.5">{scenario.key}</div>
                    <div className="text-xs text-gray-500 font-normal">{scenario.title}</div>
                  </div>
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
                    {model.model_name}
                  </div>
                </td>
                {threadScenarios.map(scenario => {
                  const thread = model.threads[scenario.key];
                  const cellColor = getCellColor(model.model_name, scenario.key, scenario.key);

                  return (
                    <td
                      key={scenario.key}
                      className="px-4 py-4 text-center relative"
                      onMouseEnter={() => setHoveredCell({ model: model.model_name, thread: scenario.key })}
                      onMouseLeave={() => setHoveredCell(null)}
                    >
                      <div className={`${cellColor} px-3 py-2 rounded-lg font-mono text-xs shadow-sm hover:shadow-md transition-shadow`}>
                        {thread?.error ? 'error' : thread?.classification.state || '—'}
                      </div>

                      {hoveredCell?.model === model.model_name && hoveredCell?.thread === scenario.key && thread && !thread.error && (
                        <div className="absolute left-1/2 top-full mt-2 -translate-x-1/2 bg-gray-900 text-white p-4 rounded-xl shadow-2xl z-20 w-80 text-left text-xs">
                          <div className="font-mono mb-3 text-sm border-b border-gray-700 pb-2">{model.model_name} × {scenario.key}</div>
                          <div className="space-y-1 mb-2">
                            <div><span className="text-gray-400">State:</span> {thread.classification.state}</div>
                            <div><span className="text-gray-400">Trajectory:</span> {thread.classification.trajectory}</div>
                            <div><span className="text-gray-400">Balance:</span> {thread.classification.participation_balance}</div>
                            <div><span className="text-gray-400">Quality:</span> {thread.classification.discourse_quality}</div>
                            <div><span className="text-gray-400">Phase:</span> {thread.classification.inquiry_phase}</div>
                          </div>
                          <div className="text-gray-300 text-xs border-t border-gray-700 pt-2">
                            {thread.classification.reasoning.slice(0, 120)}...
                          </div>
                          <div className="mt-2 text-gray-400">
                            Confidence: {thread.classification.confidence.toFixed(2)}
                          </div>
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
  );
}
