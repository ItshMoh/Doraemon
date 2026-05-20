import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export interface Task {
  id: string;
  title: string;
  notes: string | null;
  status: "open" | "completed";
  todo_date: string;
  reminder_start_date: string;
  timezone: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface TaskGroup {
  date: string;
  tasks: Task[];
}

export interface TaskGroupResponse {
  groups: TaskGroup[];
}

export interface ChatResponse {
  message: string;
  task_created: boolean;
  task: Task | null;
  needs_follow_up: boolean;
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/v1/chat/", { message });
  return response.data;
}

export async function listOpenTodos(): Promise<TaskGroupResponse> {
  const response = await api.get<TaskGroupResponse>("/v1/todos/open");
  return response.data;
}

export async function listHistoryTodos(): Promise<TaskGroupResponse> {
  const response = await api.get<TaskGroupResponse>("/v1/todos/history");
  return response.data;
}

export async function updateTaskTitle(taskId: string, title: string): Promise<Task> {
  const response = await api.patch<Task>(`/v1/todos/${taskId}`, { title });
  return response.data;
}

export async function completeTask(taskId: string): Promise<Task> {
  const response = await api.post<Task>(`/v1/todos/${taskId}/complete`);
  return response.data;
}
