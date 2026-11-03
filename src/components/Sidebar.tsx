import React from "react";

export function Sidebar() {
  return (
    <aside className="w-56 bg-cyber-800 border-r border-cyan-900/30 flex flex-col shrink-0">
      <div className="p-4 border-b border-cyan-900/30">
        <div className="text-xs font-semibold text-cyan-500/80 tracking-wider uppercase">
          Workspace
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-cyan-300 bg-cyan-500/10 border border-cyan-500/20">
          New Chat
        </button>
        <div className="pt-4 text-xs text-gray-600 px-3">Recent</div>
        <div className="text-xs text-gray-500 px-3 py-2 italic">No history yet</div>
      </nav>

      <div className="p-4 border-t border-cyan-900/30 text-xs text-gray-600">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          Backend ready
        </div>
      </div>
    </aside>
  );
}
