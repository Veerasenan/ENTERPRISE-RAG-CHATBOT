import type { ChatMessageItem } from "../types";
import SourceCard from "./SourceCard";

export default function ChatMessage({ message }: { message: ChatMessageItem }) {
  const isUser = message.role === "user";
  return (
    <div className={`msg-row ${isUser ? "user" : "assistant"}`}>
      <div className="msg-avatar">{isUser ? "You" : "AI"}</div>
      <div style={{ maxWidth: "480px" }}>
        <div className={`msg-bubble ${message.restricted ? "restricted" : ""}`}>{message.content}</div>
        {message.sources && message.sources.length > 0 && (
          <div className="sources-wrap">
            {message.sources.map((s, i) => (
              <SourceCard key={i} source={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
