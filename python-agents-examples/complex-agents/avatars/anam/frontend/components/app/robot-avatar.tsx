'use client';

import { useEffect, useState } from 'react';
import { useVoiceAssistant } from '@livekit/components-react';
import { cn } from '@/lib/shadcn/utils';

interface RobotAvatarProps {
  className?: string;
}

export function RobotAvatar({ className }: RobotAvatarProps) {
  const { state } = useVoiceAssistant();
  const [blinking, setBlinking] = useState(false);
  const [mouthOpen, setMouthOpen] = useState(false);

  // Blink every few seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setBlinking(true);
      setTimeout(() => setBlinking(false), 150);
    }, 3000 + Math.random() * 2000);
    return () => clearInterval(interval);
  }, []);

  // Animate mouth when speaking
  useEffect(() => {
    if (state === 'speaking') {
      const interval = setInterval(() => {
        setMouthOpen((prev) => !prev);
      }, 150);
      return () => clearInterval(interval);
    } else {
      setMouthOpen(false);
    }
  }, [state]);

  // Eye expression based on agent state
  const getEyeExpression = () => {
    if (blinking) return 'blink';
    switch (state) {
      case 'listening':
        return 'wide';
      case 'thinking':
        return 'squint';
      case 'speaking':
        return 'happy';
      default:
        return 'normal';
    }
  };

  const eyeExpr = getEyeExpression();

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <svg viewBox="0 0 300 350" className="w-full max-w-lg">
        {/* Antenna */}
        <line x1="150" y1="30" x2="150" y2="60" stroke="#D97706" strokeWidth="4" />
        <circle cx="150" cy="24" r="8" fill="#FBBF24">
          <animate
            attributeName="opacity"
            values={state === 'listening' ? '1;0.3;1' : '1'}
            dur={state === 'listening' ? '1s' : '0s'}
            repeatCount="indefinite"
          />
        </circle>

        {/* Head */}
        <rect x="60" y="60" width="180" height="160" rx="30" ry="30" fill="#F97316" />
        <rect x="70" y="70" width="160" height="140" rx="24" ry="24" fill="#FB923C" />

        {/* Left eye */}
        <rect x="95" y="105" width="40" height="40" rx="8" fill="#1E293B" />
        {eyeExpr === 'blink' ? (
          <rect x="100" y="122" width="30" height="4" rx="2" fill="#22D3EE" />
        ) : eyeExpr === 'wide' ? (
          <circle cx="115" cy="125" r="14" fill="#22D3EE">
            <animate attributeName="r" values="14;15;14" dur="1.5s" repeatCount="indefinite" />
          </circle>
        ) : eyeExpr === 'squint' ? (
          <>
            <rect x="100" y="118" width="30" height="12" rx="4" fill="#22D3EE" />
            <circle cx="108" cy="124" r="3" fill="#1E293B" />
            <circle cx="122" cy="124" r="3" fill="#1E293B">
              <animate attributeName="cx" values="122;118;122" dur="1s" repeatCount="indefinite" />
            </circle>
          </>
        ) : eyeExpr === 'happy' ? (
          <>
            <circle cx="115" cy="125" r="12" fill="#22D3EE" />
            <rect x="95" y="105" width="40" height="20" rx="8" fill="#1E293B" />
          </>
        ) : (
          <>
            <circle cx="115" cy="125" r="12" fill="#22D3EE" />
            <circle cx="118" cy="122" r="4" fill="#0E7490" />
          </>
        )}

        {/* Right eye */}
        <rect x="165" y="105" width="40" height="40" rx="8" fill="#1E293B" />
        {eyeExpr === 'blink' ? (
          <rect x="170" y="122" width="30" height="4" rx="2" fill="#22D3EE" />
        ) : eyeExpr === 'wide' ? (
          <circle cx="185" cy="125" r="14" fill="#22D3EE">
            <animate attributeName="r" values="14;15;14" dur="1.5s" repeatCount="indefinite" />
          </circle>
        ) : eyeExpr === 'squint' ? (
          <>
            <rect x="170" y="118" width="30" height="12" rx="4" fill="#22D3EE" />
            <circle cx="178" cy="124" r="3" fill="#1E293B">
              <animate attributeName="cx" values="178;182;178" dur="1s" repeatCount="indefinite" />
            </circle>
            <circle cx="192" cy="124" r="3" fill="#1E293B" />
          </>
        ) : eyeExpr === 'happy' ? (
          <>
            <circle cx="185" cy="125" r="12" fill="#22D3EE" />
            <rect x="165" y="105" width="40" height="20" rx="8" fill="#1E293B" />
          </>
        ) : (
          <>
            <circle cx="185" cy="125" r="12" fill="#22D3EE" />
            <circle cx="188" cy="122" r="4" fill="#0E7490" />
          </>
        )}

        {/* Mouth */}
        <rect x="110" y="165" width="80" height="30" rx="8" fill="#1E293B" />
        {mouthOpen ? (
          <ellipse cx="150" cy="180" rx="28" ry="10" fill="#22D3EE">
            <animate attributeName="ry" values="8;12;8" dur="0.3s" repeatCount="indefinite" />
          </ellipse>
        ) : state === 'listening' ? (
          <rect x="130" y="177" width="40" height="4" rx="2" fill="#22D3EE" />
        ) : (
          <path d="M 125 178 Q 150 188 175 178" stroke="#22D3EE" strokeWidth="3" fill="none" />
        )}

        {/* Ears / side panels */}
        <rect x="42" y="110" width="18" height="50" rx="6" fill="#F97316" />
        <rect x="240" y="110" width="18" height="50" rx="6" fill="#F97316" />

        {/* Neck */}
        <rect x="130" y="220" width="40" height="20" rx="4" fill="#D97706" />

        {/* Body */}
        <rect x="80" y="240" width="140" height="80" rx="20" ry="20" fill="#F97316" />
        <rect x="90" y="250" width="120" height="60" rx="14" ry="14" fill="#FB923C" />

        {/* Chest indicator light */}
        <circle cx="150" cy="280" r="10" fill="#1E293B" />
        <circle cx="150" cy="280" r="6" fill={
          state === 'speaking' ? '#22D3EE' :
          state === 'listening' ? '#4ADE80' :
          state === 'thinking' ? '#FBBF24' :
          '#64748B'
        }>
          <animate
            attributeName="opacity"
            values={state === 'thinking' ? '1;0.3;1' : '1;0.7;1'}
            dur={state === 'thinking' ? '0.8s' : '2s'}
            repeatCount="indefinite"
          />
        </circle>

        {/* State label */}
        <text x="150" y="340" textAnchor="middle" fill="#94A3B8" fontSize="12" fontFamily="monospace">
          {state === 'speaking' ? '[ SPEAKING ]' :
           state === 'listening' ? '[ LISTENING ]' :
           state === 'thinking' ? '[ THINKING ]' :
           '[ READY ]'}
        </text>
      </svg>
    </div>
  );
}
