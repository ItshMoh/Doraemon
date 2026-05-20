import { MessageSquare, CheckSquare, History } from "lucide-react";
import { BrowserRouter, NavLink, Navigate, Route, Routes } from "react-router-dom";

import { ChatPage } from "./pages/ChatPage";
import { HistoryPage } from "./pages/HistoryPage";
import { TodosPage } from "./pages/TodosPage";

const navItems = [
  { label: "Chat", to: "/chat", icon: MessageSquare },
  { label: "Todos", to: "/todos", icon: CheckSquare },
  { label: "History", to: "/history", icon: History },
];

export default function App() {
  return (
    <BrowserRouter>
      <main className="app-shell">
        <aside className="sidebar">
          <h1>Doraemon</h1>
          <nav>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.label}
                  to={item.to}
                  className={({ isActive }) =>
                    isActive ? "nav-button nav-button-active" : "nav-button"
                  }
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </aside>
        <section className="content">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/todos" element={<TodosPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </section>
      </main>
    </BrowserRouter>
  );
}
