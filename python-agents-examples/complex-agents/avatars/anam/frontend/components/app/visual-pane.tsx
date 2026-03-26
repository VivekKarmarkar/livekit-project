'use client';

import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { cn } from '@/lib/shadcn/utils';

interface VisualPaneProps {
  content: string;
  className?: string;
}

export function VisualPane({ content, className }: VisualPaneProps) {
  if (!content) {
    return (
      <div className={cn('flex items-center justify-center text-muted-foreground text-sm', className)}>
        Visual content will appear here when Robo has something to show you.
      </div>
    );
  }

  return (
    <div className={cn('overflow-y-auto p-6', className)}>
      <div className="prose prose-invert prose-lg max-w-none [&_.katex]:text-2xl">
        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
