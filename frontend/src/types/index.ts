export type Role = "Employee" | "Manager" | "HR";

export interface AuthUser {
  userId: string;
  email: string;
  fullName: string;
  role: Role;
  token: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: Role;
  full_name: string;
  user_id: string;
}

export interface SourceChunk {
  document_id: string;
  filename: string;
  page?: number | null;
  snippet: string;
}

export interface ChatMessageItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  restricted?: boolean;
  timestamp: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceChunk[];
  session_id: string;
  role: Role;
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  uploaded_by: string;
  allowed_roles: Role[];
  num_chunks: number;
  uploaded_at: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  num_chunks: number;
  allowed_roles: Role[];
  message: string;
}
