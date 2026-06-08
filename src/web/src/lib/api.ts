import { API_URL } from "./config";

export interface Todo {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: "low" | "medium" | "high";
  created_at: string;
  updated_at: string;
}

export interface TodoList {
  items: Todo[];
  total: number;
  pending: number;
  completed: number;
}

export interface CreateTodoPayload {
  title: string;
  description?: string;
  priority?: "low" | "medium" | "high";
}

export interface UpdateTodoPayload {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: "low" | "medium" | "high";
}

const base = `${API_URL}/api/v1`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  return res.json();
}

export const api = {
  todos: {
    list: () => request<TodoList>("/todos"),
    create: (payload: CreateTodoPayload) =>
      request<Todo>("/todos", { method: "POST", body: JSON.stringify(payload) }),
    update: (id: string, payload: UpdateTodoPayload) =>
      request<Todo>(`/todos/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
    toggle: (id: string) =>
      request<Todo>(`/todos/${id}/toggle`, { method: "PATCH" }),
    delete: (id: string) =>
      request<void>(`/todos/${id}`, { method: "DELETE" }),
  },
};
