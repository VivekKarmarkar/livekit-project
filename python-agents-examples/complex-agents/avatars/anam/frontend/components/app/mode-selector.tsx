'use client';

import { useState } from 'react';
import type { AppConfig } from '@/app-config';
import { App } from '@/components/app/app';

type AgentMode = 'realtime' | 'pipeline' | 'claude-code';

const MODE_COLORS: Record<AgentMode, string> = {
  realtime: 'bg-green-600 text-white',
  pipeline: 'bg-blue-600 text-white',
  'claude-code': 'bg-purple-600 text-white',
};

const MODE_ORDER: AgentMode[] = ['realtime', 'pipeline', 'claude-code'];

interface ModeSelectorProps {
  appConfig: AppConfig;
}

export function ModeSelector({ appConfig }: ModeSelectorProps) {
  const [mode, setMode] = useState<AgentMode>('realtime');

  const configWithMode: AppConfig = {
    ...appConfig,
    agentName: 'Robo-Intake',
  };

  const cycleMode = () => {
    setMode((current) => {
      const idx = MODE_ORDER.indexOf(current);
      return MODE_ORDER[(idx + 1) % MODE_ORDER.length];
    });
  };

  return (
    <>
      {/* Mode toggle — fixed at top-left */}
      <div className="fixed top-3 left-3 z-50 flex items-center gap-2">
        <span className="font-mono text-xs text-slate-500">Engine:</span>
        <button
          onClick={cycleMode}
          className={`rounded-full px-3 py-1 font-mono text-xs font-bold tracking-wider uppercase transition-colors ${MODE_COLORS[mode]}`}
        >
          {mode}
        </button>
      </div>
      <App key={mode} appConfig={configWithMode} agentMode={mode} />
    </>
  );
}
