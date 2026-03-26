'use client';

import { useSessionContext } from '@livekit/components-react';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { RobotAvatar } from '@/components/app/robot-avatar';
import { cn } from '@/lib/shadcn/utils';

interface AvatarPanelProps {
  className?: string;
}

export function AvatarPanel({ className }: AvatarPanelProps) {
  const { isConnected } = useSessionContext();

  return (
    <div className={cn('flex flex-col items-center justify-center gap-6 p-4', className)}>
      <RobotAvatar className="w-full max-w-2xl flex-1" />

      <AgentControlBar
        variant="livekit"
        isConnected={isConnected}
        controls={{
          microphone: true,
          leave: true,
          camera: false,
          screenShare: false,
          chat: false,
        }}
        className="w-full max-w-xl shrink-0"
      />
    </div>
  );
}
