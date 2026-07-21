import { apiClient } from "./api";
import type { DocumentInfo, Role, UploadResponse } from "../types";

export async function uploadPdf(file: File, allowedRoles: Role[]): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  allowedRoles.forEach((role) => formData.append("allowed_roles", role));

  const { data } = await apiClient.post<UploadResponse>("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const { data } = await apiClient.get<{ documents: DocumentInfo[] }>("/documents");
  return data.documents;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}
