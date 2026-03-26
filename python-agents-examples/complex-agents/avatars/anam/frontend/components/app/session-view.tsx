'use client';

import React, { useEffect, useState } from 'react';
import { useSessionContext } from '@livekit/components-react';
import type { RpcInvocationData } from 'livekit-client';
import type { AppConfig } from '@/app-config';
import { AvatarPanel } from '@/components/app/avatar-panel';
import { VisualPane } from '@/components/app/visual-pane';

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  void appConfig;
  const { room, isConnected } = useSessionContext();
  const [visualMode, setVisualMode] = useState(false);
  const [visualContent, setVisualContent] = useState('');

  // Register RPC handler for showContent
  useEffect(() => {
    if (!room || !isConnected) return;

    room.registerRpcMethod('showContent', async (data: RpcInvocationData) => {
      const { content } = JSON.parse(data.payload) as { content: string };
      setVisualContent(content);
      setVisualMode(true);
      return JSON.stringify({ success: true });
    });

    return () => {
      room.unregisterRpcMethod('showContent');
    };
  }, [room, isConnected]);

  return (
    <section
      className="bg-background relative flex h-full w-full flex-col overflow-hidden"
      style={{ zIndex: 'var(--app-z-session)' }}
      {...props}
    >
      {/* Toggle button */}
      <div className="absolute top-3 right-3 z-10">
        <button
          onClick={() => setVisualMode((prev) => !prev)}
          className={`rounded-full px-3 py-1.5 font-mono text-xs font-bold tracking-wider uppercase transition-colors ${
            visualMode
              ? 'bg-orange-500 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          {visualMode ? 'Visual ON' : 'Visual OFF'}
        </button>
      </div>

      {visualMode ? (
        /* Two-pane layout: robot left, visual right */
        <div className="flex min-h-0 flex-1 flex-col md:flex-row">
          <div className="flex w-full min-w-0 shrink-0 flex-col border-b md:w-[40%] md:border-r md:border-b-0">
            <AvatarPanel className="flex-1" />
          </div>
          <div className="flex min-h-0 min-w-0 flex-1 flex-col">
            <VisualPane content={visualContent} className="flex-1" />
          </div>
        </div>
      ) : (
        /* Chat mode: robot fills the screen */
        <div className="flex min-h-0 flex-1 items-center justify-center">
          <AvatarPanel className="w-full max-w-lg flex-1" />
        </div>
      )}
    </section>
  );
};
