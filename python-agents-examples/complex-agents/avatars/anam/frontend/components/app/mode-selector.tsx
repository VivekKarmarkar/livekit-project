'use client';

import { useState } from 'react';
import type { AppConfig } from '@/app-config';
import { App } from '@/components/app/app';

interface ModeSelectorProps {
  appConfig: AppConfig;
}

export function ModeSelector({ appConfig }: ModeSelectorProps) {
  const [mode, setMode] = useState<'realtime' | 'pipeline'>('realtime');

  // Pass mode as a query parameter that the connection-details route reads
  const configWithMode: AppConfig = {
    ...appConfig,
    agentName: 'Robo-Intake',
  };

  return (
    <>
      {/* Mode toggle — fixed at top-left */}
      <div className="fixed top-3 left-3 z-50 flex items-center gap-2">
        <span className="font-mono text-xs text-slate-500">Engine:</span>
        <button
          onClick={() => setMode((m) => (m === 'realtime' ? 'pipeline' : 'realtime'))}
          className={`rounded-full px-3 py-1 font-mono text-xs font-bold tracking-wider uppercase transition-colors ${
            mode === 'realtime'
              ? 'bg-green-600 text-white'
              : 'bg-blue-600 text-white'
          }`}
        >
          {mode}
        </button>
      </div>
      <App key={mode} appConfig={configWithMode} agentMode={mode} />
    </>
  );
}
