interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function Sidebar({
  activeSection,
  onSectionChange
}: SidebarProps) {
  const sections = [
    { id: 'runs', label: 'Runs' },
    { id: 'trigger', label: 'Trigger run' },
  ];

  return (
    <div className="w-72 bg-[#f3f4f6] border-r border-gray-300 h-screen flex flex-col p-5 shadow-sm">
      <div className="mb-6 border-b border-gray-300 pb-5">
        <div className="text-[10px] uppercase tracking-[0.24em] text-gray-500 mb-2">
          AI Discussion Moderation
        </div>
        <h1 className="text-lg text-gray-900 mb-1">Dashboard</h1>
        <div className="text-xs text-gray-500">Runs, traces, and pipeline checks</div>
      </div>

      <div className="mb-5">
        <label className="text-[10px] text-gray-500 uppercase tracking-[0.2em] block mb-3">Views</label>
        <div className="space-y-1.5">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => onSectionChange(section.id)}
              className={`w-full text-left px-3 py-2.5 text-sm rounded-md transition-all border ${
                activeSection === section.id
                  ? 'bg-[#31414a] border-[#31414a] text-white shadow-sm'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-100'
              }`}
            >
              {section.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
