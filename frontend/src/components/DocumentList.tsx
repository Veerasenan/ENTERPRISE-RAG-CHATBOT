import { useState } from "react";
import { deleteDocument } from "../api/uploadApi";
import type { DocumentInfo } from "../types";

interface Props {
  documents: DocumentInfo[];
  onChanged: () => void;
}

export default function DocumentList({ documents, onChanged }: Props) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  async function handleDelete(id: string) {
    if (!confirm("Delete this document and all its indexed content?")) return;
    setDeletingId(id);
    try {
      await deleteDocument(id);
      onChanged();
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="card">
      <h2>Uploaded documents ({documents.length})</h2>
      {documents.length === 0 ? (
        <p style={{ fontSize: 13.5, color: "var(--gray-500)" }}>No documents uploaded yet.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Visible to</th>
              <th>Chunks</th>
              <th>Uploaded</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.document_id}>
                <td>{doc.filename}</td>
                <td>
                  {doc.allowed_roles.map((r) => (
                    <span className="role-chip" key={r}>{r}</span>
                  ))}
                </td>
                <td>{doc.num_chunks}</td>
                <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                <td>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(doc.document_id)}
                    disabled={deletingId === doc.document_id}
                  >
                    {deletingId === doc.document_id ? "Deleting..." : "Delete"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
