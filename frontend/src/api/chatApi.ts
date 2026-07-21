import { apiClient } from "./api";
import type { ChatResponse } from "../types";

export interface SendMessageParams {
  question: string;
  sessionId: string;
}

export async function sendMessage({ question, sessionId }: SendMessageParams): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>("/chat", {
    question,
    session_id: sessionId,
  });
  return data;
}

/** Streams tokens from /chat/stream (SSE) — used for the "live typing" effect. */
export async function streamMessage(
  { question, sessionId }: SendMessageParams,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (message: string) => void
): Promise<void> {
  const token = sessionStorage.getItem("access_token");
  try {
    const response = await fetch(`${apiClient.defaults.baseURL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ question, session_id: sessionId }),
    });

    if (!response.ok || !response.body) {
      onError(`Request failed (${response.status})`);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        try {
          const payload = JSON.parse(line.replace("data:", "").trim());
          if (payload.token) onToken(payload.token);
          if (payload.done) onDone();
          if (payload.error) onError(payload.error);
        } catch {
          /* ignore malformed chunk */
        }
      }
    }
    onDone();
  } catch (err) {
    onError(err instanceof Error ? err.message : "Streaming failed");
  }
}
