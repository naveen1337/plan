import type { KeyboardEvent } from "react";
import { TextArea } from "../../components/inputs/react/text-area";
import { Button } from "../../components/buttons/react/button";
import type { ChatMessage } from "./chat_ctrl";
import { CHAT_INPUT_PLACEHOLDER, CHAT_INPUT_ROWS } from "./chat_ctrl";

export interface ChatUiProps {
  messages: ChatMessage[];
  draft: string;
  canSend: boolean;
  onDraftChange: (value: string) => void;
  onSend: () => void;
}

export function ChatUi({
  messages,
  draft,
  canSend,
  onDraftChange,
  onSend,
}: ChatUiProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-bg text-light">
      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <p className="m-auto text-sm text-muted">No messages yet. Start the conversation below.</p>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="flex justify-end">
              <div className="max-w-[70%] whitespace-pre-wrap break-words rounded-sm bg-surface-hover px-4 py-2 text-sm text-light">
                {message.text}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="flex items-end gap-3 border-t border-border bg-surface p-4">
        <TextArea
          aria-label="Message"
          placeholder={CHAT_INPUT_PLACEHOLDER}
          rows={CHAT_INPUT_ROWS}
          size="md"
          value={draft}
          onChange={(e) => onDraftChange(e.target.value)}
          onKeyDown={handleKeyDown}
          className="min-w-0 flex-1"
        />
        <Button kind="primary" size="md" onClick={onSend} disabled={!canSend}>
          Send
        </Button>
      </div>
    </div>
  );
}
