import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  timestamp: number;
}

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  currentAgents: Record<string, string>; // agent -> status
  selectedModel: string;
  battleMode: boolean;
  conversationId: string;

  setModel: (model: string) => void;
  toggleBattleMode: () => void;
  sendMessage: (text: string) => Promise<void>;
  addMessage: (msg: Omit<Message, "id" | "timestamp">) => void;
  updateLastAssistant: (content: string) => void;
  setAgentStatus: (agent: string, status: string) => void;
}

const API_BASE = "http://127.0.0.1:8742";

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  currentAgents: {},
  selectedModel: "claude-3-5-sonnet-20241022",
  battleMode: false,
  conversationId: crypto.randomUUID(),

  setModel: (model) => set({ selectedModel: model }),
  toggleBattleMode: () => set((s) => ({ battleMode: !s.battleMode })),

  addMessage: (msg) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { ...msg, id: crypto.randomUUID(), timestamp: Date.now() },
      ],
    })),

  updateLastAssistant: (content) =>
    set((s) => {
      const msgs = [...s.messages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === "assistant") {
        msgs[msgs.length - 1] = { ...last, content };
      }
      return { messages: msgs };
    }),

  setAgentStatus: (agent, status) =>
    set((s) => ({
      currentAgents: { ...s.currentAgents, [agent]: status },
    })),

  sendMessage: async (text: string) => {
    const { selectedModel, conversationId, battleMode, addMessage, updateLastAssistant, setAgentStatus } = get();

    addMessage({ role: "user", content: text });
    addMessage({ role: "assistant", content: "" });
    set({ isStreaming: true, currentAgents: {} });

    try {
      const res = await fetch(`${API_BASE}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          conversation_id: conversationId,
          model: selectedModel,
          enable_swarm: !battleMode,
          battle_mode: battleMode,
        }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data === "[DONE]") continue;

            try {
              const event = JSON.parse(data);

              if (event.type === "token") {
                fullContent += event.content;
                updateLastAssistant(fullContent);
              } else if (event.type === "agent_status") {
                setAgentStatus(event.agent, event.status);
              } else if (event.type === "status") {
                // optional UI toast
              } else if (event.type === "final") {
                updateLastAssistant(event.content);
              } else if (event.type === "battle") {
                // handled separately in BattleMode
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
    } catch (err: any) {
      updateLastAssistant(`⚠️ Error: ${err.message || "Failed to reach backend. Is it running on :8742?"}`);
    } finally {
      set({ isStreaming: false });
    }
  },
}));
