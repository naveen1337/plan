import { useState } from "react";
import type { ChatMessage } from "./chat_ctrl";
import { ChatUi } from "./chat_ui";

export function ChatScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");

  const text = draft.trim();
  const canSend = text.length > 0;

  const handleSend = () => {
    if (!canSend) return;
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), text }]);
    setDraft("");
  };

  return (
    <ChatUi
      messages={messages}
      draft={draft}
      canSend={canSend}
      onDraftChange={setDraft}
      onSend={handleSend}
    />
  );
}
