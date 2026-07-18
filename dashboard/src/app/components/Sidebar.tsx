interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function Sidebar({
  activeSection,
  onSectionChange
}: SidebarProps) {
  const sections = [
    { id: 'trigger', label: 'New run' },
    { id: 'runs', label: 'Runs' },
  ];

  return (
    <div className="w-72 bg-dashboard-surface border-r border-border h-screen flex flex-col p-5">
      <div className="mb-6 border-b border-border pb-5">
        <div className="text-label uppercase tracking-ui text-muted-foreground mb-2">
          AI Discussion Moderation
        </div>
        <div className="text-lg font-semibold text-foreground mb-1">Dashboard</div>
        <p className="text-xs text-muted-foreground">Create a run, then review the results</p>
      </div>

      <div className="mb-5">
        <div className="text-label text-muted-foreground uppercase tracking-ui-sm block mb-3">Pages</div>
        <div className="space-y-1.5">
          {sections.map((section) => (
            <button
              type="button"
              key={section.id}
              onClick={() => onSectionChange(section.id)}
              className={`w-full text-left px-3 py-2.5 text-sm rounded-md transition-all border ${
                activeSection === section.id
                  ? 'bg-dashboard-panel border-dashboard-panel text-white shadow-sm'
                  : 'bg-background border-border text-muted-foreground hover:bg-muted'
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
