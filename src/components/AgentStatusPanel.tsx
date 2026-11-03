import React from "react";
import clsx from "clsx";

interface Props {
  agents: Record<string, string>;
}

const AGENT_LABELS: Record<string, string> = {
  code_architect: "Code",
  research: "Research",
  data_analyst: "Data",
  creative_vision: "Creative",
  orchestrator: "Orchestrator",
};

export function AgentStatusPanel({ agents }: Props) {
  const entries = Object.entries(agents);
  if (entries.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      {entries.map(([agent, status]) => (
        <div
          key={agent}
          className={clsx(
            "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border",
            status === "running" || status === "synthesizing"
              ? "bg-cyan-500/10 border-cyan-500/40 text-cyan-300"
              : status === "completed"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : "bg-gray-800 border-gray-700 text-gray-400"
          )}
        >
          {(status === "running" || status === "synthesizing") && (
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse" />
          )}
          {AGENT_LABELS[agent] || agent}
        </div>
      ))}
    </div>
  );
}
