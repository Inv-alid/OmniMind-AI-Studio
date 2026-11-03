import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "../stores/chatStore";
import clsx from "clsx";

interface Props {
  messages: Message[];
  isStreaming: boolean;
}

export function ChatWindow({ messages, isStreaming }: Props) {
  return (
    <div className="h-full overflow-y-auto px-4 py-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            <div className="text-5xl mb-4 opacity-30">◈</div>
            <h2 className="text-xl font-medium text-gray-400 mb-2">OmniMind AI Studio</h2>
            <p className="text-sm">Multi-Agent Swarm • Universal LLM Router • Local RAG</p>
            <p className="text-xs mt-4 text-gray-600">Start by asking anything. The swarm will decide which agents to activate.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={clsx(
              "flex",
              msg.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={clsx(
                "max-w-[85%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed",
                msg.role === "user"
                  ? "bg-cyan-600/20 border border-cyan-500/30 text-cyan-50"
                  : "bg-cyber-700 border border-cyan-900/30 text-gray-200"
              )}
            >
              {msg.role === "assistant" ? (
                <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-cyber-900 prose-pre:border prose-pre:border-cyan-900/40">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content || (isStreaming ? "▌" : "")}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              )}
            </div>
          </div>
        ))}

        {isStreaming && messages[messages.length - 1]?.content === "" && (
          <div className="flex justify-start">
            <div className="bg-cyber-700 border border-cyan-900/30 rounded-2xl px-5 py-3.5">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
