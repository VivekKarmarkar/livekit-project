import { Button } from '@/components/ui/button';

function WelcomeImage() {
  return (
    <div className="mb-4 flex size-64 items-center justify-center overflow-hidden rounded-lg border-4 border-orange-300 bg-slate-950 dark:border-orange-600">
      <svg viewBox="0 0 200 220" className="w-40">
        <line x1="100" y1="15" x2="100" y2="35" stroke="#D97706" strokeWidth="3" />
        <circle cx="100" cy="10" r="6" fill="#FBBF24" />
        <rect x="35" y="35" width="130" height="110" rx="22" fill="#F97316" />
        <rect x="43" y="43" width="114" height="94" rx="17" fill="#FB923C" />
        <rect x="60" y="65" width="28" height="28" rx="6" fill="#1E293B" />
        <circle cx="74" cy="79" r="9" fill="#22D3EE" />
        <rect x="112" y="65" width="28" height="28" rx="6" fill="#1E293B" />
        <circle cx="126" cy="79" r="9" fill="#22D3EE" />
        <rect x="72" y="108" width="56" height="18" rx="6" fill="#1E293B" />
        <path d="M 82 117 Q 100 124 118 117" stroke="#22D3EE" strokeWidth="2.5" fill="none" />
        <rect x="85" y="145" width="30" height="14" rx="3" fill="#D97706" />
        <rect x="50" y="159" width="100" height="50" rx="14" fill="#F97316" />
        <rect x="58" y="167" width="84" height="34" rx="10" fill="#FB923C" />
        <circle cx="100" cy="184" r="7" fill="#1E293B" />
        <circle cx="100" cy="184" r="4" fill="#4ADE80" />
      </svg>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <WelcomeImage />

        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          Chat with Robo about anything
          <br />
          Powered by LiveKit
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-6 w-64 rounded-full font-mono text-xs font-bold tracking-wider uppercase"
        >
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Need help getting set up? Check out the{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="underline"
          >
            Voice AI quickstart
          </a>
          .
        </p>
      </div>
    </div>
  );
};
