import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Send, Settings, Radio } from 'lucide-react';

export default function Header({ status, onOpenSettings }) {
  const [gmtTime, setGmtTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setGmtTime(now.toUTCString().slice(17, 25) + ' GMT');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-12 bg-[#151921] border-b border-[#222834] px-4 flex items-center justify-between select-none">
      {/* Brand & Connection State */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00E676] animate-pulse" />
          <span className="font-bold text-sm tracking-wide text-white">THE LIFE</span>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-[#222834] text-[#00F0FF] font-mono font-medium">
          CONFLUENCE TERMINAL v1.0
        </span>

        <div className="hidden md:flex items-center space-x-2 pl-3 border-l border-[#222834] text-xs text-gray-400">
          <span>Broker:</span>
          <span className="text-gray-200 font-mono font-semibold">FTMO • MT5 #827192</span>
        </div>
      </div>

      {/* Center Clock & Protection Shield */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#0B0E14] border border-[#222834] text-xs font-mono text-[#00E676]">
          <ShieldCheck className="w-3.5 h-3.5 text-[#00E676]" />
          <span>PROP FIRM SHIELD: SAFE</span>
        </div>

        <div className="hidden lg:flex items-center space-x-1.5 text-xs font-mono text-gray-300">
          <Activity className="w-3.5 h-3.5 text-[#00F0FF]" />
          <span>{gmtTime || '14:00:00 GMT'}</span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3 text-xs">
        {status?.user_paused && (
          <span className="px-2 py-0.5 bg-[#D500F9]/20 text-[#D500F9] border border-[#D500F9] rounded font-mono font-semibold">
            TERMINAL PAUSED
          </span>
        )}

        <button
          onClick={onOpenSettings}
          className="flex items-center space-x-1.5 px-3 py-1 rounded bg-[#222834] hover:bg-[#30363D] transition text-gray-300 hover:text-white"
        >
          <Settings className="w-3.5 h-3.5" />
          <span>Settings</span>
        </button>
      </div>
    </header>
  );
}
