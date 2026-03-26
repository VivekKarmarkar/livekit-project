'use client';

import React, { useEffect, useState } from 'react';
import { useSessionContext } from '@livekit/components-react';
import type { RpcInvocationData } from 'livekit-client';
import type { AppConfig } from '@/app-config';
import { AvatarPanel } from '@/components/app/avatar-panel';
import { VisualPane } from '@/components/app/visual-pane';
import { BlackboardPane } from '@/components/app/blackboard-pane';

type ViewMode = 'chill' | 'visual' | 'blackboard';

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  void appConfig;
  const { room, isConnected } = useSessionContext();

  // Existing visual mode state
  const [visualMode, setVisualMode] = useState(false);
  const [visualContent, setVisualContent] = useState('');

  // Blackboard mode
  const [blackboardMode, setBlackboardMode] = useState(false);

  // Slideshow state (add-on) — accumulates all show_content calls as slides
  const [slides, setSlides] = useState<string[]>([]);
  const [slideIndex, setSlideIndex] = useState(0);

  const viewMode: ViewMode = blackboardMode ? 'blackboard' : visualMode ? 'visual' : 'chill';

  // Existing showContent RPC handler — COMPLETELY UNCHANGED
  useEffect(() => {
    if (!room || !isConnected) return;

    room.registerRpcMethod('showContent', async (data: RpcInvocationData) => {
      const { content } = JSON.parse(data.payload) as { content: string };
      setVisualContent(content);
      // Add to slides
      setSlides((prev) => {
        const next = [...prev, content];
        setSlideIndex(next.length - 1);
        return next;
      });
      // Only auto-switch to visual if not already on blackboard
      setBlackboardMode((bb) => {
        if (!bb) setVisualMode(true);
        return bb;
      });
      return JSON.stringify({ success: true });
    });

    return () => {
      room.unregisterRpcMethod('showContent');
    };
  }, [room, isConnected]);

  const showTwoPane = viewMode === 'visual' || viewMode === 'blackboard';
  const currentSlide = slides.length > 0 ? slides[slideIndex] : visualContent;

  return (
    <section
      className="bg-background relative flex h-full w-full flex-col overflow-hidden"
      style={{ zIndex: 'var(--app-z-session)' }}
      {...props}
    >
      {/* Mode toggles */}
      <div className="absolute top-3 right-3 z-10 flex gap-1">
        <button
          onClick={() => { setVisualMode(false); setBlackboardMode(false); }}
          className={`rounded-full px-3 py-1.5 font-mono text-xs font-bold tracking-wider uppercase transition-colors ${
            viewMode === 'chill'
              ? 'bg-orange-500 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          chill
        </button>
        <button
          onClick={() => { setVisualMode(true); setBlackboardMode(false); }}
          className={`rounded-full px-3 py-1.5 font-mono text-xs font-bold tracking-wider uppercase transition-colors ${
            viewMode === 'visual'
              ? 'bg-orange-500 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          visual
        </button>
        <button
          onClick={() => { setBlackboardMode(true); setVisualMode(false); }}
          className={`rounded-full px-3 py-1.5 font-mono text-xs font-bold tracking-wider uppercase transition-colors ${
            viewMode === 'blackboard'
              ? 'bg-orange-500 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          blackboard
        </button>
      </div>

      {showTwoPane ? (
        <div className="flex min-h-0 flex-1 flex-col md:flex-row">
          <div className="flex w-full min-w-0 shrink-0 flex-col border-b md:w-[40%] md:border-r md:border-b-0">
            <AvatarPanel className="flex-1" />
          </div>
          <div className="flex min-h-0 min-w-0 flex-1 flex-col">
            {viewMode === 'visual' ? (
              <VisualPane content={currentSlide} className="flex-1" />
            ) : (
              <BlackboardPane content={currentSlide} className="flex-1" />
            )}
            {/* Slide navigation (add-on) */}
            {slides.length > 1 && (
              <div className="flex items-center justify-center gap-3 border-t border-slate-800 px-4 py-2">
                <button
                  onClick={() => setSlideIndex((i) => Math.max(0, i - 1))}
                  disabled={slideIndex === 0}
                  className="rounded px-2 py-1 font-mono text-xs text-slate-400 hover:text-white disabled:text-slate-700 transition-colors"
                >
                  &larr; prev
                </button>
                <span className="font-mono text-xs text-slate-500">
                  {slideIndex + 1} / {slides.length}
                </span>
                <button
                  onClick={() => setSlideIndex((i) => Math.min(slides.length - 1, i + 1))}
                  disabled={slideIndex === slides.length - 1}
                  className="rounded px-2 py-1 font-mono text-xs text-slate-400 hover:text-white disabled:text-slate-700 transition-colors"
                >
                  next &rarr;
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 items-center justify-center">
          <AvatarPanel className="w-full max-w-lg flex-1" />
        </div>
      )}
    </section>
  );
};
