import React from "react";

export function BattleMode() {
  return (
    <div className="h-full flex items-center justify-center text-gray-500">
      <div className="text-center">
        <div className="text-4xl mb-3 opacity-40">⚔</div>
        <h2 className="text-lg font-medium text-gray-400">Battle Mode</h2>
        <p className="text-sm mt-2 max-w-md">
          Send a prompt to compare answers from multiple models side-by-side.
          <br />
          (Full split-view coming in next iteration)
        </p>
      </div>
    </div>
  );
}
