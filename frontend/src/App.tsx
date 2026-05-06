import { MessageSquare, CheckSquare, History } from "lucide-react";

import { ChatPage } from "./pages/ChatPage";

const navItems = [
  { label: "Chat", icon: MessageSquare },
  { label: "Todos", icon: CheckSquare },
  { label: "History", icon: History },
];

export default function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <h1>Doraemon</h1>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <button className="nav-button" key={item.label}>
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <section className="content">
        <ChatPage />
      </section>
    </main>
  );
}
