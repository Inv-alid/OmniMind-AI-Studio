import React, { useEffect, useRef, useState } from "react";
import { useChatStore } from "./stores/chatStore";
import { ModelSelector } from "./components/ModelSelector";
import { AgentStatusPanel } from "./components/AgentStatusPanel";
import { ChatWindow } from "./components/ChatWindow";
import { Sidebar } from "./components/Sidebar";
import { BattleMode } from "./components/BattleMode";

export default function App() {
  const {
    messages,
    isStreaming,
    currentAgents,
    selectedModel,
    battleMode,
    sendMessage,
    setModel,
    toggleBattleMode,
  } = useChatStore();

  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;
    const text = input;
    setInput("");
    await sendMessage(text);
  };

  return (
    <div className="h-screen w-screen bg-cyber-900 text-gray-100 flex overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-14 border-b border-cyan-900/40 bg-cyber-800/90 backdrop-blur flex items-center justify-between px-5 shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-semibold tracking-tight">
              <span className="text-cyan-400">OmniMind</span>{" "}
              <span className="text-gray-500 font-normal">AI Studio</span>
            </h1>
            <ModelSelector value={selectedModel} onChange={setModel} />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleBattleMode}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition border ${
                battleMode
                  ? "bg-fuchsia-600/20 text-fuchsia-300 border-fuchsia-500/50"
                  : "bg-cyber-700 text-gray-400 border-transparent hover:bg-cyber-600"
              }`}
            >
              {battleMode ? "⚔ Battle ON" : "Battle Mode"}
            </button>
            <AgentStatusPanel agents={currentAgents} />
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-hidden relative">
          {battleMode ? (
            <BattleMode />
          ) : (
            <ChatWindow messages={messages} isStreaming={isStreaming} />
          )}
          <div ref={bottomRef} />
        </main>

        {/* Input area */}
        <footer className="border-t border-cyan-900/30 bg-cyber-800 p-4 shrink-0">
          <div className="max-w-4xl mx-auto flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask the swarm anything... (Shift+Enter for new line)"
              className="flex-1 bg-cyber-700 border border-cyan-900/40 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 placeholder:text-gray-600 transition"
              rows={2}
              disabled={isStreaming}
            />
            <button
              onClick={handleSend}
              disabled={isStreaming || !input.trim()}
              className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl font-medium text-sm transition shadow-lg shadow-cyan-900/40 active:scale-95"
            >
              {isStreaming ? (
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                  Thinking
                </span>
              ) : (
                "Send"
              )}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}