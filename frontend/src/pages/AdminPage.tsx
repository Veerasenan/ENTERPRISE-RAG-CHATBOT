import { useCallback, useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import UploadPanel from "../components/UploadPanel";
import DocumentList from "../components/DocumentList";
import { listDocuments } from "../api/uploadApi";
import type { DocumentInfo } from "../types";

export default function AdminPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <div className="page-container">
          <div className="page-header">
            <h1>Manage policy documents</h1>
            <p>Upload company policy PDFs and control which roles can see each one.</p>
          </div>

          <UploadPanel onUploaded={refresh} />
          {!loading && <DocumentList documents={documents} onChanged={refresh} />}
        </div>
      </div>
    </div>
  );
}
