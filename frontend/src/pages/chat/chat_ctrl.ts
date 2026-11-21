import type { NodeCategory } from "../../components/side-bars/react/node-sidebar";

export interface ChatMessage {
  id: string;
  text: string;
}

export const CHAT_PRODUCT_NAME = "Plan and Execution";
export const CHAT_SIDEBAR_FOOTER = "Chat history";
export const CHAT_INPUT_ROWS = 2;
export const CHAT_INPUT_PLACEHOLDER = "Type a message... (Enter to send, Shift+Enter for a new line)";

export const CHAT_SIDEBAR_CATEGORIES: NodeCategory[] = [
  {
    id: "chats",
    label: "Chats",
    items: [
      { id: "chat-1", label: "Plan review", recent: true },
      { id: "chat-2", label: "Skill authoring", recent: true },
      { id: "chat-3", label: "Backend routes" },
    ],
  },
];
