import React, { useState } from 'react';
import { Send, Zap, XOctagon, ShieldCheck, Edit3, Check } from 'lucide-react';

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

  // Editable Account Balance (defaults to $10,000 or status)
  const [customBalance, setCustomBalance] = useState(() => {
    const saved = localStorage.getItem('the_life_user_balance');
    return saved ? parseFloat(saved) : (status?.account_balance || 10000.0);
  });
  const [isEditingBalance, setIsEditingBalance] = useState(false);
  const [tempBalanceInput, setTempBalanceInput] = useState(customBalance.toString());

  const dailyPnl = status?.daily_pnl_usd !== undefined ? status.daily_pnl_usd : 0.0;
  const equity = customBalance + dailyPnl;
  const tradesToday = status?.trades_taken_today !== undefined ? status.trades_taken_today : 0;
  const maxTrades = status?.max_trades_per_day || 2;

  // Dynamic Institutional Lot Calculator based on Active Symbol, Balance, and Risk %
  const calculateLots = (sym, bal, riskPct) => {
    const riskDollars = bal * (riskPct / 100);
    let total = 0.03;

    if (sym === 'XAUUSD') {
      // 30 pips risk ($3.00/oz), $10/pip -> $300 risk per lot
      total = Math.max(0.03, Math.round((riskDollars / 300) * 100) / 100);
    } else if (sym === 'BTCUSD') {
      // $500 risk distance -> $500 risk per lot
      total = Math.max(0.03, Math.round((riskDollars / 500) * 100) / 100);
    } else if (sym === 'EURUSD' || sym === 'GBPUSD') {
      // 15 pips risk, $10/pip -> $150 risk per lot
      total = Math.max(0.03, Math.round((riskDollars / 150) * 100) / 100);
    } else if (sym === 'XAGUSD') {
      // 20 pips risk ($0.20/oz), $50/pip -> $1,000 risk per lot
      total = Math.max(0.03, Math.round((riskDollars / 1000) * 100) / 100);
    }

    const tLot = (total / 3).toFixed(2);
    return { totalLot: total.toFixed(2), trancheLot: tLot };
  };

  const { totalLot, trancheLot } = calculateLots(symbol, customBalance, riskPercent);

  const handleSaveBalance = () => {
    const val = parseFloat(tempBalanceInput);
    if (!isNaN(val) && val > 0) {
      setCustomBalance(val);
      localStorage.setItem('the_life_user_balance', val.toString());
    }
    setIsEditingBalance(false);
  };

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
          {/* Editable Balance */}
          <div className="flex items-center space-x-1.5">
            <span className="text-gray-400">Balance: </span>
            {isEditingBalance ? (
              <div className="flex items-center space-x-1">
                <input
                  type="number"
                  value={tempBalanceInput}
                  onChange={(e) => setTempBalanceInput(e.target.value)}
                  className="w-24 px-1.5 py-0.5 bg-[#0B0E14] border border-[#00F0FF] rounded text-white text-xs font-bold font-mono outline-none"
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && handleSaveBalance()}
                />
                <button
                  onClick={handleSaveBalance}
                  className="p-1 rounded bg-[#00E676] text-black hover:bg-[#00C853]"
                >
                  <Check className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <div
                onClick={() => {
                  setTempBalanceInput(customBalance.toString());
                  setIsEditingBalance(true);
                }}
                className="flex items-center space-x-1 cursor-pointer group"
                title="Click to edit account balance"
              >
                <span className="font-bold text-white group-hover:text-[#00F0FF]">
                  ${customBalance.toLocaleString()}
                </span>
                <Edit3 className="w-3 h-3 text-gray-500 group-hover:text-[#00F0FF]" />
              </div>
            )}
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

        {/* Risk Selector & Dynamic Lot Sizing */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">Risk:</span>
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
          </div>

          <div className="text-gray-400 pl-3 border-l border-[#222834]">
            3-Tranche Split:{' '}
            <span className="text-[#00F0FF] font-bold">
              3x {trancheLot} Lot
            </span>{' '}
            <span className="text-gray-500 text-[10px]">({totalLot} Lot Total)</span>
          </div>
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

          {/* Close All Button */}
          <button
            onClick={onCloseAll}
            className="h-full px-3.5 rounded-lg bg-[#0B0E14] border border-[#FF3B30] text-[#FF3B30] hover:bg-[#FF3B30]/10 font-bold text-xs font-mono transition flex items-center justify-center space-x-1"
          >
            <XOctagon className="w-3.5 h-3.5" />
            <span>CLOSE ALL</span>
          </button>

          {/* Telegram Dispatch Button */}
          <button
            disabled={sendingAlert}
            onClick={handleTelegram}
            className="h-full px-3.5 rounded-lg bg-[#0B0E14] border border-[#00F0FF] text-[#00F0FF] hover:bg-[#00F0FF]/10 font-bold text-xs font-mono transition flex items-center justify-center space-x-1"
          >
            <Send className="w-3.5 h-3.5" />
            <span>DISPATCH TELEGRAM</span>
          </button>
        </div>

        {/* Live Positions Table */}
        <div className="flex-1 rounded-lg bg-[#0B0E14] border border-[#222834] overflow-hidden flex flex-col">
          <div className="h-6 bg-[#181E27] px-3 flex items-center justify-between text-[10px] font-mono text-gray-400 uppercase tracking-wider">
            <span>Open Tranches Monitor</span>
            <span>Live MT5 Telemetry</span>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {openPositions.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs font-mono text-gray-500">
                NO OPEN TRANCHES • WAITING FOR INSTITUTIONAL CONFLUENCE SETUP
              </div>
            ) : (
              <div className="space-y-1 text-xs font-mono">
                {openPositions.map((pos) => (
                  <div
                    key={pos.package_id}
                    className="p-1.5 rounded bg-[#151921] border border-[#222834] flex items-center justify-between"
                  >
                    <span className="font-bold text-[#00F0FF]">{pos.package_id}</span>
                    <span className={pos.direction === 'BUY' ? 'text-[#00E676]' : 'text-[#FF3B30]'}>
                      {pos.direction} {pos.symbol}
                    </span>
                    <span className="text-gray-300">Entry: {pos.entry_price}</span>
                    <span className="text-gray-300">SL: {pos.active_sl}</span>
                    <span className="text-[#00E676]">TP1: {pos.tp1_price}</span>
                    <span className="text-[#00C853]">TP2: {pos.tp2_price}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#00E676]/10 text-[#00E676] font-bold">
                      {pos.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
