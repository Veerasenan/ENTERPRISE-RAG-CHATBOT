import type { SourceChunk } from "../types";

export default function SourceCard({ source }: { source: SourceChunk }) {
  return (
    <div className="source-card">
      <div className="source-title">
        {source.filename}
        {source.page ? ` · page ${source.page}` : ""}
      </div>
      <div>{source.snippet}...</div>
    </div>
  );
}
