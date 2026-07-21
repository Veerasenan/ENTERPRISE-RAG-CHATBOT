import { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { streamMessage } from "../api/chatApi";
import { useAuth } from "../context/AuthContext";
import type { ChatMessageItem } from "../types";
import ChatMessage from "./ChatMessage";

const NO_CONTEXT_PHRASE = "not available to your role";

export default function ChatWindow() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const sessionId = useRef(uuidv4()).current;
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isStreaming) return;

    const userMsg: ChatMessageItem = {
      id: uuidv4(),
      role: "user",
      content: question,
      timestamp: Date.now(),
    };
    const assistantId = uuidv4();
    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: assistantId, role: "assistant", content: "", timestamp: Date.now() },
    ]);
    setInput("");
    setIsStreaming(true);

    let accumulated = "";
    await streamMessage(
      { question, sessionId },
      (token) => {
        accumulated += token;
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, content: accumulated } : m))
        );
      },
      () => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, restricted: accumulated.toLowerCase().includes(NO_CONTEXT_PHRASE) }
              : m
          )
        );
        setIsStreaming(false);
      },
      (errMsg) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: `Error: ${errMsg}`, restricted: true } : m
          )
        );
        setIsStreaming(false);
      }
    );
  }

  return (
    <>
      <div className="chat-header">
        <h1>Company Policy Assistant</h1>
      </div>

      <div className="chat-body" ref={bodyRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="icon">💬</div>
            <h3>Ask about company policy</h3>
            <p>
              Signed in as <strong>{user?.role}</strong> — answers are automatically scoped to what
              your role is permitted to see.
            </p>
          </div>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {isStreaming && (
          <div className="msg-row assistant">
            <div className="msg-avatar">AI</div>
            <div className="msg-bubble typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-bar">
        <input
          type="text"
          placeholder="Ask about leave, payroll, or HR policy..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={isStreaming}
        />
        <button className="send-btn" onClick={handleSend} disabled={isStreaming || !input.trim()}>
          {isStreaming ? <Loader /> : "→"}
        </button>
      </div>
    </>
  );
}

function Loader() {
  return <span className="spinner" />;
}
