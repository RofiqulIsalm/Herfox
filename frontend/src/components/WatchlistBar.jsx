import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Clock } from 'lucide-react';

export default function WatchlistBar({ watchlist, activeSymbol, onSelectSymbol }) {
  const defaultList = [
    { symbol: 'XAUUSD', bid: 4069.69, ask: 4069.87, change_24h_percent: -0.45, spread_pips: 1.8, max_spread_pips: 3.0 },
    { symbol: 'BTCUSD', bid: 75868.00, ask: 75873.00, change_24h_percent: 1.25, spread_pips: 5.0, max_spread_pips: 25.0 },
    { symbol: 'EURUSD', bid: 1.08740, ask: 1.08755, change_24h_percent: -0.12, spread_pips: 1.5, max_spread_pips: 1.5 },
    { symbol: 'GBPUSD', bid: 1.29870, ask: 1.29890, change_24h_percent: 0.22, spread_pips: 2.0, max_spread_pips: 2.0 },
    { symbol: 'XAGUSD', bid: 32.740, ask: 32.765, change_24h_percent: -0.33, spread_pips: 2.5, max_spread_pips: 4.0 },
  ];

  const items = (watchlist && watchlist.length > 0) ? watchlist : defaultList;

  return (
    <div className="w-64 bg-[#151921] border-r border-[#222834] flex flex-col h-full select-none">
      {/* Title */}
      <div className="px-3 py-2 border-b border-[#222834] flex items-center justify-between text-xs text-gray-400 font-semibold tracking-wider uppercase">
        <span>Watchlist (Zone B)</span>
        <span className="text-[10px] text-[#00F0FF]">M15 CORE</span>
      </div>

      {/* Asset Cards List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {items.map((item) => {
          const isActive = item.symbol === activeSymbol;
          const isUp = item.change_24h_percent >= 0;
          const isFx = item.symbol.includes('USD') && !item.symbol.includes('XAU') && !item.symbol.includes('XAG') && !item.symbol.includes('BTC');

          return (
            <div
              key={item.symbol}
              onClick={() => onSelectSymbol(item.symbol)}
              className={`p-2.5 rounded cursor-pointer transition border ${
                isActive
                  ? 'bg-[#1C222D] border-[#00F0FF] shadow-lg shadow-[#00F0FF]/10'
                  : 'bg-[#0B0E14] border-[#222834] hover:border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white font-mono">{item.symbol}</span>
                <span
                  className={`text-xs font-mono font-medium flex items-center space-x-0.5 ${
                    isUp ? 'text-[#00E676]' : 'text-[#FF3B30]'
                  }`}
                >
                  {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  <span>{isUp ? `+${item.change_24h_percent}%` : `${item.change_24h_percent}%`}</span>
                </span>
              </div>

              <div className="flex items-baseline justify-between mt-1 text-xs font-mono">
                <span className="text-gray-300 font-semibold">
                  {typeof item.bid === 'number' ? item.bid.toFixed(isFx ? 5 : 2) : item.bid}
                </span>
                <span className="text-gray-500 text-[11px]">
                  Spr: <span className={item.spread_veto ? 'text-[#FF3B30] font-bold' : 'text-gray-300'}>{item.spread_pips} p</span>
                </span>
              </div>

              {item.spread_veto && (
                <div className="mt-1 flex items-center space-x-1 text-[10px] text-[#FF3B30] font-bold">
                  <AlertTriangle className="w-3 h-3" />
                  <span>SPREAD VETO ACTIVE</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ForexFactory News Guard Status Card */}
      <div className="p-3 border-t border-[#222834] bg-[#0D1117]">
        <div className="flex items-center justify-between text-xs font-mono text-gray-400">
          <span className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-[#FFB300]" />
            <span>NEWS GUARD</span>
          </span>
          <span className="text-[10px] text-[#00E676] font-bold px-1.5 py-0.5 rounded bg-[#00E676]/10">
            ACTIVE
          </span>
        </div>
        <div className="mt-1.5 text-xs text-gray-300 font-mono">
          <span>Next Red Folder:</span>
          <p className="text-[#00F0FF] font-semibold text-[11px] truncate">US Non-Farm Payrolls</p>
          <span className="text-gray-400 text-[10px]">Release in: ~4h 12m</span>
        </div>
      </div>
    </div>
  );
}
