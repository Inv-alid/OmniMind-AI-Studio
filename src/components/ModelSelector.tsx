import React, { useEffect, useState } from "react";

interface Model {
  id: string;
  provider: string;
}

interface Props {
  value: string;
  onChange: (model: string) => void;
}

const FALLBACK_MODELS: Model[] = [
  { id: "claude-3-5-sonnet-20241022", provider: "anthropic" },
  { id: "gpt-4o", provider: "openai" },
  { id: "gpt-4o-mini", provider: "openai" },
  { id: "grok-2", provider: "xai" },
  { id: "gemini-1.5-pro", provider: "google" },
  { id: "deepseek-chat", provider: "deepseek" },
  { id: "llama3.3", provider: "local" },
];

export function ModelSelector({ value, onChange }: Props) {
  const [models, setModels] = useState<Model[]>(FALLBACK_MODELS);

  useEffect(() => {
    fetch("http://127.0.0.1:8742/api/models/")
      .then((r) => r.json())
      .then((data) => {
        if (data.models?.length) setModels(data.models);
      })
      .catch(() => {});
  }, []);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-cyber-700 border border-cyan-900/40 text-sm rounded-lg px-3 py-1.5 text-gray-200 focus:outline-none focus:border-cyan-500/60 max-w-[220px]"
    >
      {models.map((m) => (
        <option key={m.id} value={m.id}>
          {m.id} ({m.provider})
        </option>
      ))}
    </select>
  );
}
