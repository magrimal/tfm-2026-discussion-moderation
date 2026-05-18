import { useState } from 'react';
import { Save, Plus, Trash2 } from 'lucide-react';

interface PipelineConfig {
  models: {
    name: string;
    enabled: boolean;
    temperature: number;
    max_tokens: number;
  }[];
  evaluation_criteria: {
    classification_weight: number;
    intervention_weight: number;
    response_quality_weight: number;
  };
  logfuse_endpoint: string;
  output_directory: string;
}

export function Configuration() {
  const [config, setConfig] = useState<PipelineConfig>({
    models: [
      { name: 'claude-opus-4-7', enabled: true, temperature: 0.3, max_tokens: 4096 },
      { name: 'claude-sonnet-4-6', enabled: true, temperature: 0.3, max_tokens: 4096 },
      { name: 'gpt-4-turbo', enabled: true, temperature: 0.3, max_tokens: 4096 },
      { name: 'gpt-4o', enabled: false, temperature: 0.3, max_tokens: 4096 }
    ],
    evaluation_criteria: {
      classification_weight: 0.4,
      intervention_weight: 0.3,
      response_quality_weight: 0.3
    },
    logfuse_endpoint: 'https://logfuse.io/api/v1',
    output_directory: './runs'
  });

  const [newModelName, setNewModelName] = useState('');

  const updateModel = (index: number, field: string, value: any) => {
    const newModels = [...config.models];
    newModels[index] = { ...newModels[index], [field]: value };
    setConfig({ ...config, models: newModels });
  };

  const addModel = () => {
    if (newModelName.trim()) {
      setConfig({
        ...config,
        models: [...config.models, {
          name: newModelName,
          enabled: true,
          temperature: 0.3,
          max_tokens: 4096
        }]
      });
      setNewModelName('');
    }
  };

  const removeModel = (index: number) => {
    setConfig({
      ...config,
      models: config.models.filter((_, i) => i !== index)
    });
  };

  const handleSave = () => {
    // Mock save action
    alert('Configuration saved successfully!');
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl text-gray-900">Pipeline Configuration</h2>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-[#5A9FA8] text-white rounded hover:bg-[#4A8F98] transition-colors"
        >
          <Save className="w-4 h-4" />
          Save Configuration
        </button>
      </div>

      <div className="space-y-6">
        {/* Models Configuration */}
        <div className="bg-white border border-gray-300 rounded p-6">
          <h3 className="text-lg mb-4 text-gray-900">Models</h3>

          <div className="space-y-3 mb-4">
            {config.models.map((model, idx) => (
              <div key={idx} className="flex items-center gap-4 p-3 bg-gray-50 rounded">
                <input
                  type="checkbox"
                  checked={model.enabled}
                  onChange={(e) => updateModel(idx, 'enabled', e.target.checked)}
                  className="w-4 h-4"
                />
                <div className="flex-1 font-mono text-sm">{model.name}</div>
                <div className="flex items-center gap-2">
                  <label className="text-xs text-gray-600">Temperature:</label>
                  <input
                    type="number"
                    value={model.temperature}
                    onChange={(e) => updateModel(idx, 'temperature', parseFloat(e.target.value))}
                    step="0.1"
                    min="0"
                    max="1"
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-xs text-gray-600">Max tokens:</label>
                  <input
                    type="number"
                    value={model.max_tokens}
                    onChange={(e) => updateModel(idx, 'max_tokens', parseInt(e.target.value))}
                    step="512"
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
                <button
                  onClick={() => removeModel(idx)}
                  className="p-1 text-[#C0392B] hover:bg-red-50 rounded"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newModelName}
              onChange={(e) => setNewModelName(e.target.value)}
              placeholder="Model name (e.g., claude-haiku-4-5)"
              className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
              onKeyPress={(e) => e.key === 'Enter' && addModel()}
            />
            <button
              onClick={addModel}
              className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm"
            >
              <Plus className="w-4 h-4" />
              Add Model
            </button>
          </div>
        </div>

        {/* Evaluation Criteria */}
        <div className="bg-white border border-gray-300 rounded p-6">
          <h3 className="text-lg mb-4 text-gray-900">Evaluation Criteria Weights</h3>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-700">Classification Accuracy</label>
                <span className="font-mono text-sm text-gray-600">
                  {config.evaluation_criteria.classification_weight.toFixed(1)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.evaluation_criteria.classification_weight}
                onChange={(e) => setConfig({
                  ...config,
                  evaluation_criteria: {
                    ...config.evaluation_criteria,
                    classification_weight: parseFloat(e.target.value)
                  }
                })}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-700">Intervention Accuracy</label>
                <span className="font-mono text-sm text-gray-600">
                  {config.evaluation_criteria.intervention_weight.toFixed(1)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.evaluation_criteria.intervention_weight}
                onChange={(e) => setConfig({
                  ...config,
                  evaluation_criteria: {
                    ...config.evaluation_criteria,
                    intervention_weight: parseFloat(e.target.value)
                  }
                })}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-700">Response Quality</label>
                <span className="font-mono text-sm text-gray-600">
                  {config.evaluation_criteria.response_quality_weight.toFixed(1)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.evaluation_criteria.response_quality_weight}
                onChange={(e) => setConfig({
                  ...config,
                  evaluation_criteria: {
                    ...config.evaluation_criteria,
                    response_quality_weight: parseFloat(e.target.value)
                  }
                })}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Integration Settings */}
        <div className="bg-white border border-gray-300 rounded p-6">
          <h3 className="text-lg mb-4 text-gray-900">Integration Settings</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-700 mb-2">LogFuse Endpoint</label>
              <input
                type="text"
                value={config.logfuse_endpoint}
                onChange={(e) => setConfig({ ...config, logfuse_endpoint: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm font-mono"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-2">Output Directory</label>
              <input
                type="text"
                value={config.output_directory}
                onChange={(e) => setConfig({ ...config, output_directory: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm font-mono"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
