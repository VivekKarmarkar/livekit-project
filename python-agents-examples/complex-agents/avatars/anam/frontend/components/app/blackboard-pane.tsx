'use client';

import { useEffect, useRef, useState } from 'react';
import { Streamdown } from 'streamdown';
import { cn } from '@/lib/shadcn/utils';

interface BlackboardPaneProps {
  content: string;
  className?: string;
}

export function BlackboardPane({ content, className }: BlackboardPaneProps) {
  const [revealed, setRevealed] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const indexRef = useRef(0);
  const prevContentRef = useRef('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!content) return;

    // Only animate when NEW content arrives, not on remount with existing content
    if (content === prevContentRef.current) return;

    // If remounting with existing content (was revealed before), show it all immediately
    if (prevContentRef.current === '' && revealed === '' && content.length > 0 && indexRef.current === 0) {
      // Check if this is a remount by seeing if content was already set before
      // On first mount with new content: animate. On remount with same content: show all.
    }

    prevContentRef.current = content;
    indexRef.current = 0;
    setRevealed('');
    setIsStreaming(true);

    const interval = setInterval(() => {
      indexRef.current += 3;
      if (indexRef.current >= content.length) {
        indexRef.current = content.length;
        setIsStreaming(false);
        clearInterval(interval);
      }
      setRevealed(content.slice(0, indexRef.current));
    }, 15);

    return () => clearInterval(interval);
  }, [content]);

  // Auto-scroll during streaming
  useEffect(() => {
    if (isStreaming && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [revealed, isStreaming]);

  // If component mounts with content but nothing revealed yet (remount case), show all
  useEffect(() => {
    if (content && !revealed && !isStreaming && prevContentRef.current === '') {
      prevContentRef.current = content;
      setRevealed(content);
    }
  }, []);

  if (!content) {
    return (
      <div className={cn('flex flex-col items-center justify-center gap-2 text-slate-500 text-sm', className)}>
        <span className="font-mono text-xs tracking-wider uppercase">[ Blackboard ]</span>
        <span>Ask Robo to explain something — content will stream live here.</span>
      </div>
    );
  }

  return (
    <div className={cn('overflow-y-auto px-6 pt-12 pb-4', className)}>
      <style>{`
        .blackboard-content .katex { font-size: 2.5rem !important; }
        .blackboard-content .katex-display { font-size: 3rem !important; margin: 1.5rem 0 !important; }
      `}</style>
      <div className="blackboard-content">
        <Streamdown
          isAnimating={isStreaming}
          mermaid={{ config: { theme: 'dark' } }}
        >
          {revealed || content}
        </Streamdown>
      </div>
      <div ref={bottomRef} />
    </div>
  );
}
