import { useState } from 'react';
import { Play, Plus, FileText, Zap } from 'lucide-react';

interface Thread {
  thread_id: string;
  title: string;
  scenario_type: string;
  post_count: number;
  is_synthetic: boolean;
}

const mockThreads: Thread[] = [
  { thread_id: 'thread_001', title: 'Introduction to machine learning', scenario_type: 'new', post_count: 2, is_synthetic: false },
  { thread_id: 'thread_002', title: 'Neural network architectures', scenario_type: 'active', post_count: 12, is_synthetic: false },
  { thread_id: 'thread_003', title: 'Open source licensing', scenario_type: 'stalled', post_count: 8, is_synthetic: false },
  { thread_id: 'thread_004', title: 'Regulation of AI in the EU', scenario_type: 'conflictive', post_count: 15, is_synthetic: false },
  { thread_id: 'thread_005', title: 'Data preprocessing best practices', scenario_type: 'convergent', post_count: 10, is_synthetic: false },
  { thread_id: 'thread_006', title: 'Weekend plans and course deadlines', scenario_type: 'off_topic', post_count: 6, is_synthetic: false },
];

export function Trigger() {
  const [selectedThreads, setSelectedThreads] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>(['claude-opus-4-7', 'claude-sonnet-4-6', 'gpt-4-turbo']);
  const [runName, setRunName] = useState('');
  const [showSyntheticForm, setShowSyntheticForm] = useState(false);
  const [syntheticThread, setSyntheticThread] = useState({
    title: '',
    scenario_type: 'active',
    content: ''
  });
  const [isRunning, setIsRunning] = useState(false);

  const availableModels = ['claude-opus-4-7', 'claude-sonnet-4-6', 'gpt-4-turbo', 'gpt-4o'];

  const toggleThread = (threadId: string) => {
    if (selectedThreads.includes(threadId)) {
      setSelectedThreads(selectedThreads.filter(id => id !== threadId));
    } else {
      setSelectedThreads([...selectedThreads, threadId]);
    }
  };

  const toggleModel = (model: string) => {
    if (selectedModels.includes(model)) {
      setSelectedModels(selectedModels.filter(m => m !== model));
    } else {
      setSelectedModels([...selectedModels, model]);
    }
  };

  const handleTriggerRun = () => {
    if (selectedThreads.length === 0 || selectedModels.length === 0) {
      alert('Please select at least one thread and one model');
      return;
    }

    setIsRunning(true);

    // Mock execution
    setTimeout(() => {
      setIsRunning(false);
      alert(`Pipeline run started!\nRun: ${runName || 'Untitled run'}\nThreads: ${selectedThreads.length}\nModels: ${selectedModels.length}\n\nResults will appear in the run overview once complete.`);
    }, 2000);
  };

  const handleCreateSynthetic = () => {
    if (!syntheticThread.title || !syntheticThread.content) {
      alert('Please fill in all fields');
      return;
    }

    alert(`Synthetic thread "${syntheticThread.title}" created successfully!`);
    setShowSyntheticForm(false);
    setSyntheticThread({ title: '', scenario_type: 'active', content: '' });
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl mb-6 text-gray-900">Trigger Run</h2>

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column: Thread Selection */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-300 rounded p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg text-gray-900">Select Threads</h3>
              <button
                onClick={() => setShowSyntheticForm(!showSyntheticForm)}
                className="flex items-center gap-2 px-3 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm"
              >
                <Plus className="w-4 h-4" />
                Synthetic
              </button>
            </div>

            <div className="space-y-2 mb-4">
              {mockThreads.map(thread => (
                <label
                  key={thread.thread_id}
                  className="flex items-center gap-3 p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedThreads.includes(thread.thread_id)}
                    onChange={() => toggleThread(thread.thread_id)}
                    className="w-4 h-4"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-900">{thread.title}</span>
                      {thread.is_synthetic && (
                        <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">
                          synthetic
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                      <span className="font-mono">{thread.thread_id}</span>
                      <span>•</span>
                      <span>{thread.scenario_type}</span>
                      <span>•</span>
                      <span>{thread.post_count} posts</span>
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <div className="text-xs text-gray-600">
              {selectedThreads.length} thread(s) selected
            </div>
          </div>

          {showSyntheticForm && (
            <div className="bg-white border border-gray-300 rounded p-6">
              <h3 className="text-lg mb-4 text-gray-900">Create Synthetic Thread</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-700 mb-2">Thread Title</label>
                  <input
                    type="text"
                    value={syntheticThread.title}
                    onChange={(e) => setSyntheticThread({ ...syntheticThread, title: e.target.value })}
                    placeholder="E.g., Ethics in AI development"
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-700 mb-2">Scenario Type</label>
                  <select
                    value={syntheticThread.scenario_type}
                    onChange={(e) => setSyntheticThread({ ...syntheticThread, scenario_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                  >
                    <option value="new">New</option>
                    <option value="active">Active</option>
                    <option value="stalled">Stalled</option>
                    <option value="conflictive">Conflictive</option>
                    <option value="convergent">Convergent</option>
                    <option value="off_topic">Off Topic</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-700 mb-2">Thread Content (JSON or text)</label>
                  <textarea
                    value={syntheticThread.content}
                    onChange={(e) => setSyntheticThread({ ...syntheticThread, content: e.target.value })}
                    placeholder='[{"author": "Alice", "text": "..."}, {"author": "Bob", "text": "..."}]'
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm font-mono"
                  />
                </div>

                <button
                  onClick={handleCreateSynthetic}
                  className="w-full px-4 py-2 bg-[#5A9FA8] text-white rounded hover:bg-[#4A8F98] transition-colors text-sm"
                >
                  Create Synthetic Thread
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Model Selection & Trigger */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-300 rounded p-6">
            <h3 className="text-lg mb-4 text-gray-900">Select Models</h3>

            <div className="space-y-2 mb-4">
              {availableModels.map(model => (
                <label
                  key={model}
                  className="flex items-center gap-3 p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedModels.includes(model)}
                    onChange={() => toggleModel(model)}
                    className="w-4 h-4"
                  />
                  <span className="font-mono text-sm">{model}</span>
                </label>
              ))}
            </div>

            <div className="text-xs text-gray-600">
              {selectedModels.length} model(s) selected
            </div>
          </div>

          <div className="bg-white border border-gray-300 rounded p-6">
            <h3 className="text-lg mb-4 text-gray-900">Run Configuration</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-700 mb-2">Run Name (optional)</label>
                <input
                  type="text"
                  value={runName}
                  onChange={(e) => setRunName(e.target.value)}
                  placeholder={`${new Date().toISOString().split('T')[0]} — custom run`}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>

              <div className="p-4 bg-gray-50 rounded text-sm">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-700">Run Summary</span>
                </div>
                <div className="space-y-1 text-gray-600">
                  <div>Threads: <span className="font-mono">{selectedThreads.length}</span></div>
                  <div>Models: <span className="font-mono">{selectedModels.length}</span></div>
                  <div>Total checks: <span className="font-mono">{selectedThreads.length * selectedModels.length}</span></div>
                </div>
              </div>

              <button
                onClick={handleTriggerRun}
                disabled={isRunning || selectedThreads.length === 0 || selectedModels.length === 0}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#5A9FA8] text-white rounded hover:bg-[#4A8F98] transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isRunning ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Trigger Run
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-900">
            <div className="flex items-start gap-2">
              <div className="text-blue-600 mt-0.5">ℹ</div>
              <div>
                <div className="font-medium mb-1">Pipeline execution</div>
                <div className="text-blue-800">
                  Results will be logged to LogFuse and available in the run overview once the run completes.
                  Execution typically takes 2-5 minutes per model per thread.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
