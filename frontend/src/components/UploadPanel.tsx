import { useRef, useState } from "react";
import { uploadPdf } from "../api/uploadApi";
import type { Role } from "../types";

const ALL_ROLES: Role[] = ["Employee", "Manager", "HR"];

export default function UploadPanel({ onUploaded }: { onUploaded: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [selectedRoles, setSelectedRoles] = useState<Role[]>(["Employee"]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function toggleRole(role: Role) {
    setSelectedRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
    );
  }

  async function handleUpload() {
    setError(null);
    setSuccess(null);
    if (!file) {
      setError("Please choose a PDF file first.");
      return;
    }
    if (selectedRoles.length === 0) {
      setError("Select at least one role that should be able to view this document.");
      return;
    }

    setIsUploading(true);
    try {
      const res = await uploadPdf(file, selectedRoles);
      setSuccess(`"${res.filename}" indexed into ${res.num_chunks} chunks for: ${res.allowed_roles.join(", ")}`);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      onUploaded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div className="card">
      <h2>Upload policy document</h2>

      {error && <div className="form-error">{error}</div>}
      {success && (
        <div className="form-error" style={{ background: "var(--success-50)", color: "var(--success-600)" }}>
          {success}
        </div>
      )}

      <div className="dropzone" onClick={() => fileInputRef.current?.click()}>
        <div>📄 Click to choose a PDF, or drag one here</div>
        {file && <div className="file-name">{file.name}</div>}
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
      </div>

      <p style={{ fontSize: 13.5, color: "var(--gray-600)", margin: "16px 0 4px" }}>
        Who should be able to see this document?
      </p>
      <div className="checkbox-row">
        {ALL_ROLES.map((role) => (
          <label className="checkbox-item" key={role}>
            <input
              type="checkbox"
              checked={selectedRoles.includes(role)}
              onChange={() => toggleRole(role)}
            />
            {role}
          </label>
        ))}
      </div>

      <button className="btn-primary" onClick={handleUpload} disabled={isUploading}>
        {isUploading ? "Uploading and indexing..." : "Upload and index"}
      </button>
    </div>
  );
}
