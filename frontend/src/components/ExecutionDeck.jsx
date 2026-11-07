import React, { useState } from 'react';
import { Send, Zap, XOctagon, ShieldCheck } from 'lucide-react';

export default function ExecutionDeck({
  symbol,
  status,
  positions,
  onExecute,
  onCloseAll,
  onSendTelegramAlert,
}) {
  const [riskPercent, setRiskPercent] = useState(1.0);
  const [executing, setExecuting] = useState(false);
  const [sendingAlert, setSendingAlert] = useState(false);

  const balance = status?.account_balance || 10000.0;
  const equity = status?.equity || 10185.0;
  const dailyPnl = status?.daily_pnl_usd || 185.0;
  const tradesToday = status?.trades_taken_today || 1;
  const maxTrades = status?.max_trades_per_day || 2;

  const handleExecute = async (direction) => {
    setExecuting(true);
    await onExecute(direction, riskPercent);
    setExecuting(false);
  };

  const handleTelegram = async () => {
    setSendingAlert(true);
    await onSendTelegramAlert();
    setSendingAlert(false);
  };

  const openPositions = positions?.open_positions || [];

  return (
    <div className="h-44 bg-[#151921] border-t border-[#222834] flex flex-col select-none">
      {/* Top Bar: Metrics & Controls */}
      <div className="h-10 px-4 border-b border-[#222834] flex items-center justify-between text-xs font-mono">
        <div className="flex items-center space-x-6">
          <div>
            <span className="text-gray-400">Balance: </span>
            <span className="font-bold text-white">${balance.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-400">Equity: </span>
            <span className="font-bold text-[#00F0FF]">${equity.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-400">Today PnL: </span>
            <span className={`font-bold ${dailyPnl >= 0 ? 'text-[#00E676]' : 'text-[#FF3B30]'}`}>
              {dailyPnl >= 0 ? `+$${dailyPnl.toFixed(2)}` : `-$${Math.abs(dailyPnl).toFixed(2)}`}
            </span>
          </div>
          <div>
            <span className="text-gray-400">Daily Trades: </span>
            <span className="font-bold text-white">
              [ {tradesToday} / {maxTrades} Max ]
            </span>
          </div>
        </div>

        {/* Risk Selector & Sizing */}
        <div className="flex items-center space-x-3">
          <span className="text-gray-400">Risk %:</span>
          <div className="flex items-center space-x-1">
            {[0.5, 1.0, 2.0].map((r) => (
              <button
                key={r}
                onClick={() => setRiskPercent(r)}
                className={`px-2 py-0.5 rounded text-[11px] font-bold transition ${
                  riskPercent === r
                    ? 'bg-[#00F0FF] text-black'
                    : 'bg-[#222834] text-gray-300 hover:text-white'
                }`}
              >
                {r}%
              </button>
            ))}
          </div>

          <span className="text-gray-500 pl-2 border-l border-[#222834]">
            3-Tranche Split: <span className="text-white font-semibold">3x 0.06 Lot</span>
          </span>
        </div>
      </div>

      {/* Action Buttons & Positions Split */}
      <div className="flex-1 flex p-2.5 gap-3">
        {/* Buttons Panel */}
        <div className="flex items-center space-x-2">
          {/* BUY Button */}
          <button
            disabled={executing || tradesToday >= maxTrades}
            onClick={() => handleExecute('BUY')}
            className="h-full px-5 rounded-lg bg-[#00E676] hover:bg-[#00C853] text-black font-extrabold text-xs font-mono transition flex items-center justify-center space-x-1.5 shadow-lg shadow-[#00E676]/20 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Zap className="w-4 h-4 fill-current" />
            <span>EXECUTE 3-TRANCHE BUY</span>
          </button>

          {/* SELL Button */}
          <button
            disabled={executing || tradesToday >= maxTrades}
            onClick={() => handleExecute('SELL')}
            className="h-full px-5 rounded-lg bg-[#FF3B30] hover:bg-[#D32F2F] text-white font-extrabold text-xs font-mono transition flex items-center justify-center space-x-1.5 shadow-lg shadow-[#FF3B30]/20 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Zap className="w-4 h-4 fill-current" />
            <span>EXECUTE 3-TRANCHE SELL</span>
          </button>

          {/* Close All */}
          <button
            onClick={onCloseAll}
            className="h-full px-3.5 rounded-lg bg-[#222834] hover:bg-[#FF3B30]/20 hover:border-[#FF3B30] border border-[#30363D] text-gray-300 hover:text-[#FF3B30] font-mono text-xs font-semibold transition flex items-center justify-center space-x-1"
          >
            <XOctagon className="w-4 h-4" />
            <span>CLOSE ALL</span>
          </button>

          {/* Telegram Alert */}
          <button
            disabled={sendingAlert}
            onClick={handleTelegram}
            className="h-full px-3.5 rounded-lg bg-[#00F0FF]/15 hover:bg-[#00F0FF]/25 border border-[#00F0FF]/40 text-[#00F0FF] font-mono text-xs font-semibold transition flex items-center justify-center space-x-1"
          >
            <Send className="w-4 h-4" />
            <span>{sendingAlert ? 'DISPATCHING...' : 'DISPATCH TELEGRAM'}</span>
          </button>
        </div>

        {/* Live Positions Table */}
        <div className="flex-1 bg-[#0B0E14] border border-[#222834] rounded-lg overflow-y-auto p-2">
          {openPositions.length === 0 ? (
            <div className="h-full flex items-center justify-center text-xs font-mono text-gray-500">
              NO OPEN TRANCHES • WAITING FOR INSTITUTIONAL CONFLUENCE SETUP
            </div>
          ) : (
            <div className="space-y-1">
              {openPositions.map((o) => (
                <div
                  key={o.ticket_id}
                  className="px-2.5 py-1 rounded bg-[#151921] border border-[#222834] flex items-center justify-between text-xs font-mono"
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-[#00F0FF] font-bold">#{o.ticket_id}</span>
                    <span className="font-semibold text-white">{o.symbol}</span>
                    <span className={o.direction === 'BUY' ? 'text-[#00E676]' : 'text-[#FF3B30]'}>
                      {o.direction}
                    </span>
                    <span className="text-gray-400">({o.lot_size} lot)</span>
                  </div>

                  <div className="flex items-center space-x-4">
                    <span className="text-gray-400">Entry: {o.entry_price}</span>
                    <span className="text-gray-400">SL: {o.sl_price}</span>
                    <span className="text-gray-400">TP: {o.tp_price || 'TRAIL'}</span>
                    <span className="text-[#00E676] font-bold">ACTIVE</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
