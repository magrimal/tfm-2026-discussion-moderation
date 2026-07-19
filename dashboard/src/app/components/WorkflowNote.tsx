interface WorkflowNoteProps {
  title?: string;
  steps: string[];
}

export function WorkflowNote({
  title = 'Help',
  steps,
}: WorkflowNoteProps) {
  if (steps.length === 0) {
    return null;
  }

  return (
    <details open className="mb-6 rounded-xl border border-status-passed-border bg-status-passed-bg px-4 py-3">
      <summary className="cursor-pointer list-none inline-flex items-center gap-2 rounded-md border border-status-passed bg-status-passed px-3 py-1.5 text-sm font-medium text-white">
        <span className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-white/40 bg-white/10 text-xs text-white">?</span>
        {title}
      </summary>
      <ol className="mt-3 space-y-1 text-sm text-muted-foreground">
        {steps.map((step, index) => (
          <li key={step} className="flex items-start gap-2">
            <span className="font-mono text-xs text-foreground mt-0.5">
              {index + 1}.
            </span>
            <span>{step}</span>
          </li>
        ))}
      </ol>
    </details>
  );
}
