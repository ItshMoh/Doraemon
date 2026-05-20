import { useEffect, useState } from "react";

import { TaskGroup, listHistoryTodos } from "../services/api";

function formatDate(iso: string): string {
  const [year, month, day] = iso.split("-").map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

export function HistoryPage() {
  const [groups, setGroups] = useState<TaskGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await listHistoryTodos();
        setGroups(data.groups);
      } catch {
        setError("Failed to load history.");
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <h2>History</h2>
      </header>

      {loading && <p className="muted">Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && groups.length === 0 && (
        <p className="muted">No completed todos yet.</p>
      )}

      {groups.map((group) => (
        <section className="task-group" key={group.date}>
          <h3 className="task-group-date">{formatDate(group.date)}</h3>
          <ul className="task-list">
            {group.tasks.map((task) => (
              <li className="task-item task-item-completed" key={task.id}>
                <span className="task-title">{task.title}</span>
                {task.completed_at && (
                  <span className="task-completed-at">
                    Completed {new Date(task.completed_at).toLocaleDateString()}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
