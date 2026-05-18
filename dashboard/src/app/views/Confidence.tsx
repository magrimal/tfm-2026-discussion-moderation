import { ModelResult } from '../types';
import { threadScenarios } from '../data/mockData';

interface ConfidenceProps {
  models: ModelResult[];
}

export function Confidence({ models }: ConfidenceProps) {
  const getAverageConfidence = (model: ModelResult, type: 'classification' | 'intervention' | 'role' | 'response') => {
    const threads = Object.values(model.threads).filter(t => !t.error);
    if (threads.length === 0) return 0;

    let sum = 0;
    let count = 0;

    threads.forEach(thread => {
      if (type === 'classification') {
        sum += thread.classification.confidence;
        count++;
      } else if (type === 'intervention') {
        sum += thread.intervention.confidence;
        count++;
      } else if (type === 'role' && thread.role_confidence !== undefined) {
        sum += thread.role_confidence;
        count++;
      } else if (type === 'response' && thread.response?.confidence !== undefined) {
        sum += thread.response.confidence;
        count++;
      }
    });

    return count > 0 ? sum / count : 0;
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl mb-6 text-gray-900">Confidence</h2>

      <div className="bg-white border border-gray-300 rounded p-6 mb-8">
        <h3 className="text-sm text-gray-600 mb-4">Per-model average confidence</h3>

        <div className="space-y-4">
          {models.map(model => {
            const confidences = {
              classification: getAverageConfidence(model, 'classification'),
              intervention: getAverageConfidence(model, 'intervention'),
              role: getAverageConfidence(model, 'role'),
              response: getAverageConfidence(model, 'response')
            };

            return (
              <div key={model.model_name} className="flex items-center gap-4">
                <div className="w-48 font-mono text-xs text-gray-700">{model.model_name}</div>
                <div className="flex gap-4 flex-1">
                  <div className="flex items-center gap-2">
                    <div
                      className="rounded-full bg-[#5A9FA8]"
                      style={{
                        width: `${Math.max(8, confidences.classification * 24)}px`,
                        height: `${Math.max(8, confidences.classification * 24)}px`
                      }}
                      title={`Classification: ${confidences.classification.toFixed(2)}`}
                    />
                    <span className="text-xs text-gray-500">c</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="rounded-full bg-[#27AE60]"
                      style={{
                        width: `${Math.max(8, confidences.intervention * 24)}px`,
                        height: `${Math.max(8, confidences.intervention * 24)}px`
                      }}
                      title={`Intervention: ${confidences.intervention.toFixed(2)}`}
                    />
                    <span className="text-xs text-gray-500">i</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="rounded-full bg-[#E67E22]"
                      style={{
                        width: `${Math.max(8, confidences.role * 24)}px`,
                        height: `${Math.max(8, confidences.role * 24)}px`
                      }}
                      title={`Role: ${confidences.role.toFixed(2)}`}
                    />
                    <span className="text-xs text-gray-500">r</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="rounded-full bg-[#9B59B6]"
                      style={{
                        width: `${Math.max(8, confidences.response * 24)}px`,
                        height: `${Math.max(8, confidences.response * 24)}px`
                      }}
                      title={`Response: ${confidences.response.toFixed(2)}`}
                    />
                    <span className="text-xs text-gray-500">resp</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex gap-6 mt-6 pt-4 border-t border-gray-200 text-xs text-gray-600">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#5A9FA8]" />
            <span>Classification</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#27AE60]" />
            <span>Intervention</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#E67E22]" />
            <span>Role</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#9B59B6]" />
            <span>Response</span>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-300 rounded p-6">
        <h3 className="text-sm text-gray-600 mb-4">Confidence by thread scenario</h3>

        <div className="h-96 flex items-end justify-between gap-2 border-l border-b border-gray-300 p-4">
          {threadScenarios.map(scenario => {
            // Get all confidence values for this thread across all models
            const threadConfidences: { [key: string]: number[] } = {
              classification: [],
              intervention: [],
              role: [],
              response: []
            };

            models.forEach(model => {
              const thread = model.threads[scenario.key];
              if (thread && !thread.error) {
                threadConfidences.classification.push(thread.classification.confidence);
                threadConfidences.intervention.push(thread.intervention.confidence);
                if (thread.role_confidence !== undefined) {
                  threadConfidences.role.push(thread.role_confidence);
                }
                if (thread.response?.confidence !== undefined) {
                  threadConfidences.response.push(thread.response.confidence);
                }
              }
            });

            const avgClassification = threadConfidences.classification.length > 0
              ? threadConfidences.classification.reduce((a, b) => a + b, 0) / threadConfidences.classification.length
              : 0;

            return (
              <div key={scenario.key} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex flex-col items-center gap-1">
                  {['classification', 'intervention', 'role', 'response'].map((type, idx) => {
                    const values = threadConfidences[type as keyof typeof threadConfidences];
                    const avg = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
                    const colors = ['#5A9FA8', '#27AE60', '#E67E22', '#9B59B6'];

                    return values.length > 0 ? (
                      <div
                        key={type}
                        className="w-2 rounded-full"
                        style={{
                          height: `${avg * 300}px`,
                          backgroundColor: colors[idx],
                          opacity: 0.7
                        }}
                        title={`${type}: ${avg.toFixed(2)}`}
                      />
                    ) : null;
                  })}
                </div>
                <div className="text-xs text-gray-600 font-mono -rotate-45 origin-top-left whitespace-nowrap mt-8">
                  {scenario.key}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-6 p-4 bg-gray-50 border border-gray-300 rounded text-sm text-gray-600 italic">
        Pedagogical quality scores (LLM-as-judge) will appear here once Capa 2 evaluation is implemented.
      </div>
    </div>
  );
}
