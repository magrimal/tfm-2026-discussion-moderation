import { useState } from 'react';
import { ModelResult } from '../types';
import { threadScenarios } from '../data/mockData';

interface CrossModelProps {
  models: ModelResult[];
}

export function CrossModel({ models }: CrossModelProps) {
  const [selectedThread, setSelectedThread] = useState('new');

  const scenario = threadScenarios.find(s => s.key === selectedThread);

  return (
    <div className="p-8">
      <h2 className="text-2xl mb-6 text-gray-900">Cross-model by thread</h2>

      <div className="flex gap-2 mb-6">
        {threadScenarios.map(scenario => (
          <button
            key={scenario.key}
            onClick={() => setSelectedThread(scenario.key)}
            className={`px-4 py-2 text-sm rounded transition-colors ${
              selectedThread === scenario.key
                ? 'bg-[#5A9FA8] text-white'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            {scenario.key}
          </button>
        ))}
      </div>

      <div className="bg-white border border-gray-300 rounded overflow-hidden mb-6">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-300">
            <tr>
              <th className="text-left px-4 py-3 text-gray-600">Model</th>
              <th className="text-left px-4 py-3 text-gray-600">Classified state</th>
              <th className="text-left px-4 py-3 text-gray-600">Intervene decision</th>
              <th className="text-left px-4 py-3 text-gray-600">Role</th>
              <th className="text-left px-4 py-3 text-gray-600">Technique</th>
              <th className="text-left px-4 py-3 text-gray-600">c_conf</th>
              <th className="text-left px-4 py-3 text-gray-600">Duration</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model, idx) => {
              const thread = model.threads[selectedThread];
              if (!thread) return null;

              const isCorrect = !thread.error && thread.classification.state === selectedThread;

              return (
                <tr
                  key={model.model_name}
                  className={`border-b border-gray-200 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}
                >
                  <td className="px-4 py-3 font-mono text-xs">{model.model_name}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {!thread.error && (
                        <div className={`w-2 h-2 rounded-full ${
                          isCorrect ? 'bg-[#27AE60]' : 'bg-[#C0392B]'
                        }`} />
                      )}
                      <span className="font-mono text-xs">
                        {thread.error ? 'error' : thread.classification.state}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {thread.error ? '—' : (
                      <span className={`px-2 py-1 rounded text-xs ${
                        thread.intervention.decision === 'intervene'
                          ? 'bg-[#27AE60] text-white'
                          : 'bg-gray-300 text-gray-700'
                      }`}>
                        {thread.intervention.decision}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs">{thread.error ? '—' : (thread.intervention.role || '—')}</td>
                  <td className="px-4 py-3 text-xs">{thread.error ? '—' : (thread.intervention.technique || '—')}</td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {thread.error ? '—' : thread.classification.confidence.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {thread.error ? '—' : `${thread.duration_ms}ms`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mb-3">
        <h3 className="text-lg text-gray-900 mb-4">Response texts</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {models.map(model => {
          const thread = model.threads[selectedThread];
          if (!thread || !thread.response || thread.error) return null;

          return (
            <div key={model.model_name} className="bg-white border border-gray-300 rounded p-4">
              <div className="font-mono text-xs text-gray-600 mb-3">{model.model_name}</div>
              <div className="p-3 bg-gray-50 border-l-4 border-[#5A9FA8] text-sm italic text-gray-800 max-h-48 overflow-y-auto">
                "{thread.response.text}"
              </div>
            </div>
          );
        })}
      </div>

      {models.every(m => !m.threads[selectedThread]?.response || m.threads[selectedThread]?.error) && (
        <div className="text-center py-8 text-gray-500 text-sm">
          No response texts generated for this thread
        </div>
      )}
    </div>
  );
}
