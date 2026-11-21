import { useState } from "react";
import { CHAT_SIDEBAR_CATEGORIES } from "./chat_ctrl";
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
      sidebarCategories={CHAT_SIDEBAR_CATEGORIES}
      canSend={canSend}
      onDraftChange={setDraft}
      onSend={handleSend}
    />
  );
}
