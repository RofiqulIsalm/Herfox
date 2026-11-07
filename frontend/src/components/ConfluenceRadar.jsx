import React from 'react';
import { CheckCircle2, XCircle, ShieldAlert, Zap, Globe, Cpu } from 'lucide-react';

export default function ConfluenceRadar({ confluenceData }) {
  const conf = confluenceData?.confluence || {};
  const score = conf.confluence_score || 88.4;
  const grade = conf.grade || 'GRADE_A_PLUS';
  const breakdown = conf.confluence_breakdown || {
    smc_liquidity: 30.0,
    classical_patterns: 20.0,
    mtf_alignment: 15.0,
    smt_divergence: 15.0,
    macro_hermes: 8.4,
  };
  const isApproved = conf.is_approved !== false;
  const vetos = conf.vetos || [];
  const reasons = conf.reasons || [
    'Unmitigated M15 Bullish FVG imbalance (40 pips)',
    'Asian Session Low Swept (Judas Swing)',
    'Bullish Pinbar rejection at horizontal support',
    'Aligned with H4/Daily Macro EMA Trend',
    'SMT Divergence: Silver made Higher Low',
  ];

  const hermes = confluenceData?.hermes_macro || {
    sentiment: 'BULLISH',
    bias_score: 42.0,
    rationale: 'Safe-haven accumulation driven by Middle East geopolitical risks and rate cut speculations.',
  };

  return (
    <div className="w-80 bg-[#151921] border-l border-[#222834] flex flex-col h-full select-none overflow-y-auto">
      {/* Title */}
      <div className="px-3 py-2 border-b border-[#222834] flex items-center justify-between text-xs text-gray-400 font-semibold tracking-wider uppercase">
        <span>Confluence Radar (Zone D)</span>
        <span className="flex items-center space-x-1 text-[#00E676] text-[10px]">
          <Zap className="w-3 h-3" />
          <span>REAL-TIME</span>
        </span>
      </div>

      <div className="p-3 space-y-4">
        {/* Master Score & Grade Card */}
        <div className="p-3 rounded-lg bg-[#0B0E14] border border-[#222834] text-center relative overflow-hidden">
          <div className="text-[11px] font-mono text-gray-400 uppercase tracking-widest">
            Overall Confluence Score
          </div>
          <div className="text-4xl font-extrabold font-mono text-[#00F0FF] my-1 drop-shadow-[0_0_12px_rgba(0,240,255,0.3)]">
            {score.toFixed(1)}%
          </div>

          <div className="mt-2 inline-flex items-center px-3 py-0.5 rounded-full text-xs font-mono font-bold tracking-wider bg-[#00F0FF]/15 text-[#00F0FF] border border-[#00F0FF]/40">
            {grade === 'GRADE_A_PLUS' ? '★ GRADE A+ SETUP ★' : 'GRADE A SETUP'}
          </div>

          {/* Veto Banner */}
          <div className="mt-3 pt-2.5 border-t border-[#222834]">
            {isApproved ? (
              <div className="flex items-center justify-center space-x-1.5 text-xs font-mono text-[#00E676]">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>ARBITER: APPROVED FOR EXECUTION</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-1.5 text-xs font-mono text-[#FF3B30] font-bold">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>BLOCKED BY VETO HIERARCHY</span>
              </div>
            )}
          </div>
        </div>

        {/* 5-Pillar Score Breakdown */}
        <div className="space-y-2">
          <span className="text-[11px] font-mono font-semibold text-gray-400 uppercase tracking-wider">
            Pillar Weightings Checklist
          </span>

          <div className="space-y-1.5 text-xs font-mono">
            {/* Pillar 1: SMC */}
            <div className="p-2 rounded bg-[#0D1117] border border-[#222834] flex items-center justify-between">
              <span className="text-gray-300">Pillar 1: SMC / Liquidity (30%)</span>
              <span className="font-bold text-[#00E676]">+{breakdown.smc_liquidity?.toFixed(1)} pts</span>
            </div>

            {/* Pillar 2: Patterns */}
            <div className="p-2 rounded bg-[#0D1117] border border-[#222834] flex items-center justify-between">
              <span className="text-gray-300">Pillar 2: Patterns & S/R (20%)</span>
              <span className="font-bold text-[#00E676]">+{breakdown.classical_patterns?.toFixed(1)} pts</span>
            </div>

            {/* Pillar 3: MTF */}
            <div className="p-2 rounded bg-[#0D1117] border border-[#222834] flex items-center justify-between">
              <span className="text-gray-300">Pillar 3: MTF Trend Align (15%)</span>
              <span className="font-bold text-[#00E676]">+{breakdown.mtf_alignment?.toFixed(1)} pts</span>
            </div>

            {/* Pillar 3: SMT */}
            <div className="p-2 rounded bg-[#0D1117] border border-[#222834] flex items-center justify-between">
              <span className="text-gray-300">Pillar 3: SMT Divergence (15%)</span>
              <span className="font-bold text-[#00E676]">+{breakdown.smt_divergence?.toFixed(1)} pts</span>
            </div>

            {/* Layer 0: Macro */}
            <div className="p-2 rounded bg-[#0D1117] border border-[#222834] flex items-center justify-between">
              <span className="text-gray-300">Layer 0: Hermes Macro (20%)</span>
              <span className="font-bold text-[#00F0FF]">+{breakdown.macro_hermes?.toFixed(1)} pts</span>
            </div>
          </div>
        </div>

        {/* Identified Confluence Drivers */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-mono font-semibold text-gray-400 uppercase tracking-wider">
            Active Confluence Drivers
          </span>
          <div className="p-2.5 rounded bg-[#0D1117] border border-[#222834] space-y-1.5 text-xs text-gray-300 font-mono">
            {reasons.slice(0, 4).map((r, i) => (
              <div key={i} className="flex items-start space-x-1.5">
                <span className="text-[#00E676] font-bold">✓</span>
                <span className="leading-tight text-[11px]">{r}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Hermes AI Research Brief Card */}
        <div className="p-2.5 rounded bg-[#0B0E14] border border-[#222834] space-y-1.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="flex items-center space-x-1 text-[#00F0FF] font-semibold">
              <Globe className="w-3.5 h-3.5" />
              <span>HERMES AI DOSSIER</span>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#00E676]/10 text-[#00E676] font-bold">
              {hermes.sentiment} ({hermes.bias_score > 0 ? `+${hermes.bias_score}` : hermes.bias_score})
            </span>
          </div>
          <p className="text-[11px] text-gray-400 leading-snug font-sans">
            "{hermes.rationale || 'Safe-haven accumulation driven by geopolitical risks.'}"
          </p>
        </div>
      </div>
    </div>
  );
}

