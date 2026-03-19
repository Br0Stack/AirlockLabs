import type { ChatMessage, Document, Event, Workspace } from './types';

const API_BASE = 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listWorkspaces: () => request<Workspace[]>('/workspaces'),
  createWorkspace: (payload: { name: string; description?: string }) =>
    request<Workspace>('/workspaces', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }),
  listDocuments: (workspaceId: number) => request<Document[]>(`/workspaces/${workspaceId}/documents`),
  uploadDocument: async (workspaceId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<Document>(`/workspaces/${workspaceId}/documents`, {
      method: 'POST',
      body: formData
    });
  },
  extractEvents: (workspaceId: number) =>
    request<{ created: number; events: Event[] }>(`/workspaces/${workspaceId}/extract-events`, {
      method: 'POST'
    }),
  listEvents: (workspaceId: number) => request<Event[]>(`/workspaces/${workspaceId}/events`),
  patchEvent: (eventId: number, payload: Partial<Event>) =>
    request<Event>(`/events/${eventId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }),
  chat: (workspaceId: number, content: string) =>
    request<{ user_message: ChatMessage; assistant_message: ChatMessage }>(`/workspaces/${workspaceId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    })
};
