import React, { useEffect, useRef, useState } from 'react';
import { Cpu, Zap, Trophy, RefreshCw, CheckCircle2, AlertOctagon, TrendingUp } from 'lucide-react';

export default function EvolutionArena({ onBackToTerminal }) {
  const canvasRef = useRef(null);
  const [tournament, setTournament] = useState(null);
  const [fanCurves, setFanCurves] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mutating, setMutating] = useState(false);
  const [promotingId, setPromotingId] = useState(null);
  const [hoveredVariant, setHoveredVariant] = useState(null);

  // Fetch Tournament Data and Fan Curves
  const fetchEvolutionData = async () => {
    try {
      const [resTourn, resCurves] = await Promise.all([
        fetch('/api/evolution/tournament').then((r) => r.json()).catch(() => null),
        fetch('/api/evolution/fan-curves').then((r) => r.json()).catch(() => null),
      ]);
      if (resTourn) setTournament(resTourn);
      if (resCurves) setFanCurves(resCurves);
      setLoading(false);
    } catch (e) {
      console.error('Failed to fetch evolution data:', e);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvolutionData();
  }, []);

  // Render HTML5 Canvas Multi-Line Equity Fan Chart
  useEffect(() => {
    if (!canvasRef.current || !fanCurves || !fanCurves.curves) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#0B0E14';
    ctx.fillRect(0, 0, width, height);

    // Padding
    const padLeft = 60;
    const padRight = 40;
    const padTop = 30;
    const padBottom = 40;

    const chartW = width - padLeft - padRight;
    const chartH = height - padTop - padBottom;

    // Find min and max equity across all curves
    let minEquity = 800;
    let maxEquity = 1400;
    let maxTrades = 80;

    fanCurves.curves.forEach((c) => {
      c.curve.forEach((pt) => {
        if (pt.equity < minEquity) minEquity = pt.equity;
        if (pt.equity > maxEquity) maxEquity = pt.equity;
        if (pt.trade > maxTrades) maxTrades = pt.trade;
      });
    });

    // Add 10% breathing room
    minEquity = Math.floor(minEquity * 0.95);
    maxEquity = Math.ceil(maxEquity * 1.05);

    const getX = (trade) => padLeft + (trade / maxTrades) * chartW;
    const getY = (eq) => padTop + chartH - ((eq - minEquity) / (maxEquity - minEquity)) * chartH;

    // Draw Grid & Labels
    ctx.strokeStyle = '#181E27';
    ctx.lineWidth = 1;
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.fillStyle = '#6E7681';

    // Horizontal grid lines
    const ySteps = 5;
    for (let i = 0; i <= ySteps; i++) {
      const eqVal = minEquity + (i / ySteps) * (maxEquity - minEquity);
      const y = getY(eqVal);
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(width - padRight, y);
      ctx.stroke();

      ctx.fillText(`$${Math.round(eqVal)}`, 10, y + 3);
    }

    // Origin Baseline ($1,000)
    const y1000 = getY(1000);
    ctx.strokeStyle = '#30363D';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padLeft, y1000);
    ctx.lineTo(width - padRight, y1000);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#8B949E';
    ctx.fillText('$1,000 BASELINE', width - padRight - 90, y1000 - 6);

    // Draw All Equity Curves (The Multi-Line Fan)
    fanCurves.curves.forEach((item) => {
      const isHovered = hoveredVariant === item.variant_id;
      ctx.strokeStyle = isHovered ? '#FFFFFF' : item.color;
      ctx.lineWidth = isHovered ? 2.5 : 1.2;
      ctx.shadowColor = item.color;
      ctx.shadowBlur = isHovered ? 12 : (item.total_return_pct > 25 ? 6 : 0);

      ctx.beginPath();
      item.curve.forEach((pt, idx) => {
        const x = getX(pt.trade);
        const y = getY(pt.equity);
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.shadowBlur = 0; // reset shadow
    });

    // Bottom Axis Trades Labels
    ctx.fillStyle = '#6E7681';
    for (let t = 0; t <= maxTrades; t += 20) {
      const x = getX(t);
      ctx.fillText(`${t} Trades`, x - 15, height - 15);
    }
  }, [fanCurves, hoveredVariant]);

  // Trigger New Generation Mutation
  const handleMutate = async () => {
    setMutating(true);
    try {
      const res = await fetch('/api/evolution/mutate?asset=XAUUSD&count=15', { method: 'POST' });
      await res.json();
      await fetchEvolutionData();
    } catch (e) {
      console.error('Mutation error:', e);
    }
    setMutating(false);
  };

  // Promote Challenger to Champion
  const handlePromote = async (variantId) => {
    setPromotingId(variantId);
    try {
      const res = await fetch('/api/evolution/promote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ variant_id: variantId }),
      });
      const data = await res.json();
      alert(`Success! Strategy ${variantId} is now the LIVE ACTIVE CHAMPION!`);
      await fetchEvolutionData();
    } catch (e) {
      console.error('Promotion error:', e);
    }
    setPromotingId(null);
  };

  const leaderboard = tournament?.leaderboard || [];
  const championId = tournament?.active_champion_id;

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0E14] text-[#E6EDF3] select-none overflow-y-auto">
      {/* Top Header */}
      <div className="h-12 bg-[#151921] border-b border-[#222834] px-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00F0FF] animate-ping" />
          <span className="font-extrabold text-sm text-white font-mono tracking-wider flex items-center space-x-1.5">
            <Cpu className="w-4 h-4 text-[#00F0FF]" />
            <span>AUTONOMOUS STRATEGY EVOLUTION ARENA</span>
          </span>
          <span className="text-xs px-2 py-0.5 rounded bg-[#00F0FF]/15 text-[#00F0FF] font-mono border border-[#00F0FF]/30">
            Generation #{tournament?.generation || 1}
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <button
            disabled={mutating}
            onClick={handleMutate}
            className="px-3.5 py-1.5 rounded bg-[#00F0FF] hover:bg-[#00D0DF] text-black font-extrabold text-xs font-mono transition flex items-center space-x-1.5 shadow-md shadow-[#00F0FF]/20"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${mutating ? 'animate-spin' : ''}`} />
            <span>{mutating ? 'SIMULATING...' : 'GENERATE 15 MUTATIONS'}</span>
          </button>

          <button
            onClick={onBackToTerminal}
            className="px-3 py-1.5 rounded bg-[#222834] hover:bg-[#30363D] text-gray-300 hover:text-white text-xs font-mono transition"
          >
            ← BACK TO TERMINAL
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-4 space-y-4">
        {/* Multi-Line Equity Fan Chart Container */}
        <div className="p-4 rounded-xl bg-[#151921] border border-[#222834] shadow-2xl">
          <div className="flex items-center justify-between mb-3 text-xs font-mono">
            <div>
              <span className="font-bold text-white tracking-wider uppercase">
                MULTI-STRATEGY EQUITY FAN CHART
              </span>
              <p className="text-gray-400 text-[11px]">
                Real-time cumulative equity branching from $1,000 across 80 backtested trades.
              </p>
            </div>
            <div className="flex items-center space-x-3 text-[11px] text-gray-400">
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#00F0FF]" />
                <span>Winning Alpha</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#FF3B30]" />
                <span>Culled Drawdown</span>
              </span>
            </div>
          </div>

          <div className="w-full flex justify-center bg-[#0B0E14] rounded-lg border border-[#222834] p-2">
            <canvas
              ref={canvasRef}
              width={1100}
              height={320}
              className="w-full max-w-5xl rounded"
            />
          </div>
        </div>

        {/* Tournament Leaderboard Table */}
        <div className="p-4 rounded-xl bg-[#151921] border border-[#222834]">
          <div className="flex items-center justify-between mb-3 text-xs font-mono">
            <span className="font-bold text-white tracking-wider uppercase flex items-center space-x-1.5">
              <Trophy className="w-4 h-4 text-[#FFD700]" />
              <span>TOURNAMENT LEADERBOARD (Top Mutated Candidates)</span>
            </span>
            <span className="text-gray-400 text-[11px]">
              Active Champion: <span className="text-[#FFD700] font-bold">{championId}</span>
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#222834] text-gray-400 uppercase text-[11px]">
                  <th className="py-2.5 px-3">Rank</th>
                  <th className="py-2.5 px-3">Variant ID</th>
                  <th className="py-2.5 px-3">Asset</th>
                  <th className="py-2.5 px-3">Win Rate</th>
                  <th className="py-2.5 px-3">P. Factor</th>
                  <th className="py-2.5 px-3">Max DD %</th>
                  <th className="py-2.5 px-3">Return</th>
                  <th className="py-2.5 px-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F242C]">
                {leaderboard.map((item) => {
                  const isChamp = item.variant_id === championId;
                  const isCulled = item.status === 'CULLED';

                  return (
                    <tr
                      key={item.variant_id}
                      onMouseEnter={() => setHoveredVariant(item.variant_id)}
                      onMouseLeave={() => setHoveredVariant(null)}
                      className={`hover:bg-[#1C222D] transition ${
                        isChamp ? 'bg-[#FFD700]/5 font-bold' : ''
                      }`}
                    >
                      <td className="py-2 px-3">
                        {isChamp ? (
                          <span className="text-[#FFD700]">👑 #1</span>
                        ) : (
                          <span className="text-gray-400">#{item.rank}</span>
                        )}
                      </td>
                      <td className="py-2 px-3 flex items-center space-x-2">
                        <span
                          className="w-2.5 h-2.5 rounded-full inline-block"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className={isChamp ? 'text-[#FFD700]' : 'text-white'}>
                          {item.variant_id}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-gray-300">{item.asset}</td>
                      <td className="py-2 px-3 font-semibold text-[#00E676]">{item.win_rate}%</td>
                      <td className="py-2 px-3 font-semibold text-white">{item.profit_factor}</td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            item.max_drawdown_percent <= 4.0
                              ? 'bg-[#00E676]/10 text-[#00E676]'
                              : 'bg-[#FF3B30]/10 text-[#FF3B30]'
                          }`}
                        >
                          {item.max_drawdown_percent}% {item.max_drawdown_percent <= 4.0 ? 'SAFE' : 'HIGH'}
                        </span>
                      </td>
                      <td className="py-2 px-3">
                        <span className={item.total_return_percent >= 0 ? 'text-[#00E676]' : 'text-[#FF3B30]'}>
                          {item.total_return_percent >= 0 ? `+${item.total_return_percent}%` : `${item.total_return_percent}%`}
                        </span>
                      </td>
                      <td className="py-2 px-3">
                        {isChamp ? (
                          <span className="text-[11px] px-2 py-0.5 rounded bg-[#FFD700]/15 text-[#FFD700] border border-[#FFD700]/40 font-bold">
                            ACTIVE CHAMPION
                          </span>
                        ) : isCulled ? (
                          <span className="text-[11px] px-2 py-0.5 rounded bg-[#FF3B30]/10 text-[#FF3B30] border border-[#FF3B30]/20">
                            CULLED
                          </span>
                        ) : (
                          <button
                            disabled={promotingId === item.variant_id}
                            onClick={() => handlePromote(item.variant_id)}
                            className="px-2.5 py-1 rounded bg-[#00F0FF]/15 hover:bg-[#00F0FF]/30 text-[#00F0FF] border border-[#00F0FF]/40 text-[11px] font-bold transition flex items-center space-x-1"
                          >
                            <Zap className="w-3 h-3" />
                            <span>{promotingId === item.variant_id ? 'PROMOTING...' : 'PROMOTE TO LIVE'}</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

