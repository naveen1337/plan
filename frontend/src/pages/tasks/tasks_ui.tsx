export function TasksUi() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-light">Tasks</h1>
        <p className="mt-1 text-sm text-muted">Plan, track, and manage tasks.</p>
      </div>

      <div className="rounded-sm border border-border bg-surface p-6 text-sm text-muted">
        No tasks yet.
      </div>
    </div>
  );
}
