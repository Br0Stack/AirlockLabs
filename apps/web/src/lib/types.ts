export type Workspace = {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
};

export type Document = {
  id: number;
  workspace_id: number;
  filename: string;
  file_type: string;
  path: string;
  raw_text: string;
  uploaded_at: string;
};

export type Event = {
  id: number;
  workspace_id: number;
  document_id: number;
  title: string;
  description: string;
  event_date: string | null;
  confidence_score: number;
  source_excerpt: string;
  created_at: string;
};

export type ChatMessage = {
  id: number;
  workspace_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
};
