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
    <aside className="w-72 shrink-0 h-full flex flex-col rounded-[28px] border border-white/70 bg-[rgba(255,253,248,0.86)] p-5 shadow-[0_18px_60px_rgba(31,36,48,0.08)] backdrop-blur">
      <div className="mb-6 border-b border-border/70 pb-5">
        <div className="text-label uppercase tracking-ui text-muted-foreground mb-2">
          Discussion moderation
        </div>
        <div className="text-xl font-semibold text-foreground mb-1">Review console</div>
        <p className="text-xs text-muted-foreground">Create a run, then inspect the results</p>
      </div>

      <div className="mb-5">
        <div className="text-label text-muted-foreground uppercase tracking-ui-sm block mb-3">Pages</div>
        <div className="space-y-1.5">
          {sections.map((section) => (
            <button
              type="button"
              key={section.id}
              onClick={() => onSectionChange(section.id)}
              className={`w-full text-left px-3 py-2.5 text-sm rounded-xl transition-all border ${
                activeSection === section.id
                  ? 'bg-dashboard-panel border-dashboard-panel text-white shadow-sm'
                  : 'bg-white/70 border-border/70 text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {section.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-auto border-t border-border/70 pt-4">
        <div className="text-label text-muted-foreground uppercase tracking-ui-sm block mb-3">Observability</div>
        <a
          href="https://logfire-eu.pydantic.dev/magrimal/tfm-2026-discussion-moderation"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-3 py-2.5 text-sm rounded-xl border border-border/70 bg-white/70 text-muted-foreground hover:bg-muted/80 transition-colors"
        >
          <span>Logfire</span>
          <svg className="ml-auto h-3 w-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </aside>
  );
}
