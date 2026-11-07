import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts';
import { Maximize2, Layers } from 'lucide-react';

export default function ChartView({ symbol, timeframe, onTimeframeChange, confluenceData, positions }) {
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const priceLinesRef = useRef([]);

  const [loading, setLoading] = useState(true);

  // Timeframes supported
  const timeframes = ['M5', 'M15', 'H1', 'H4', 'D1'];

  // Initialize or update Lightweight Chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      // Create chart instance
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: '#0B0E14' },
          textColor: '#C9D1D9',
          fontSize: 11,
          fontFamily: 'JetBrains Mono, monospace',
        },
        grid: {
          vertLines: { color: '#181E27', style: 1 },
          horzLines: { color: '#181E27', style: 1 },
        },
        crosshair: {
          mode: 1,
          vertLine: { color: '#00F0FF', width: 1, style: 2 },
          horzLine: { color: '#00F0FF', width: 1, style: 2 },
        },
        rightPriceScale: {
          borderColor: '#222834',
          scaleMargins: { top: 0.12, bottom: 0.15 },
        },
        timeScale: {
          borderColor: '#222834',
          timeVisible: true,
          secondsVisible: false,
        },
      });

      // Add Candlestick Series (Lightweight Charts v5 API)
      const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#00E676',
        downColor: '#FF3B30',
        borderVisible: false,
        wickUpColor: '#00E676',
        wickDownColor: '#FF3B30',
      });

      chartInstanceRef.current = chart;
      candlestickSeriesRef.current = candlestickSeries;

      // Auto-resize observer
      const resizeObserver = new ResizeObserver((entries) => {
        if (entries[0] && chartInstanceRef.current) {
          const { width, height } = entries[0].contentRect;
          if (width > 0 && height > 0) {
            chartInstanceRef.current.resize(width, height);
          }
        }
      });
      resizeObserver.observe(chartContainerRef.current);

      return () => {
        resizeObserver.disconnect();
        chart.remove();
      };
    } catch (err) {
      console.error('Failed to initialize TradingView Lightweight Chart:', err);
    }
  }, []);

  // Fetch candle data when symbol or timeframe changes
  useEffect(() => {
    setLoading(true);
    fetch(`/api/candles?symbol=${symbol}&timeframe=${timeframe}&count=80`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.candles && candlestickSeriesRef.current) {
          candlestickSeriesRef.current.setData(data.candles);
          chartInstanceRef.current?.timeScale().fitContent();
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch candles:', err);
        setLoading(false);
      });
  }, [symbol, timeframe]);

  // Update Price Lines (Entry, SL, TP1, TP2) ONLY when an active trade is open or Grade A+ setup is approved
  useEffect(() => {
    if (!candlestickSeriesRef.current) return;

    // Clear old price lines
    priceLinesRef.current.forEach((line) => {
      try {
        candlestickSeriesRef.current.removePriceLine(line);
      } catch (e) {}
    });
    priceLinesRef.current = [];

    // 1. Check for Active Open Position first (Fixed price levels, never jumps)
    const openTrades = positions?.open_positions || [];
    const activeTrade = openTrades.find((p) => p.symbol === symbol && p.status === 'ACTIVE');

    let entry = null;
    let sl = null;
    let tp1 = null;
    let tp2 = null;
    let titlePrefix = '';

    if (activeTrade) {
      entry = activeTrade.entry_price;
      sl = activeTrade.sl_price;
      tp1 = activeTrade.tp1_price;
      tp2 = activeTrade.tp2_price;
      titlePrefix = 'LIVE ';
    } else if (confluenceData?.confluence?.is_approved && confluenceData?.confluence?.grade === 'GRADE_A_PLUS') {
      // 2. Only show setup lines if Grade A+ is APPROVED by Arbiter
      const conf = confluenceData.confluence;
      entry = conf.entry_price;
      sl = conf.sl_price;
      const isBuy = conf.direction === 'BUY';
      const r = Math.abs(entry - sl);
      tp1 = isBuy ? entry + r : entry - r;
      tp2 = isBuy ? entry + r * 2.5 : entry - r * 2.5;
      titlePrefix = 'PENDING ';
    }

    // If neither active trade nor approved Grade A+ setup, keep chart completely clean (ZERO JUMPING LINES)
    if (!entry || !sl) return;

    const isFx = symbol.includes('USD') && !symbol.includes('XAU') && !symbol.includes('XAG') && !symbol.includes('BTC');
    const decimals = isFx ? 5 : 2;

    // 1. Entry Line
    const entryLine = candlestickSeriesRef.current.createPriceLine({
      price: entry,
      color: '#00F0FF',
      lineWidth: 1.5,
      lineStyle: 2,
      axisLabelVisible: true,
      title: `${titlePrefix}ENTRY: ${entry.toFixed(decimals)}`,
    });
    priceLinesRef.current.push(entryLine);

    // 2. Stop Loss Line
    const slLine = candlestickSeriesRef.current.createPriceLine({
      price: sl,
      color: '#FF3B30',
      lineWidth: 1.5,
      lineStyle: 2,
      axisLabelVisible: true,
      title: `${titlePrefix}SL: ${sl.toFixed(decimals)}`,
    });
    priceLinesRef.current.push(slLine);

    // 3. Take Profit 1 Line
    if (tp1) {
      const tp1Line = candlestickSeriesRef.current.createPriceLine({
        price: tp1,
        color: '#00E676',
        lineWidth: 1.5,
        lineStyle: 2,
        axisLabelVisible: true,
        title: `${titlePrefix}TP1: ${tp1.toFixed(decimals)}`,
      });
      priceLinesRef.current.push(tp1Line);
    }

    // 4. Take Profit 2 Line
    if (tp2) {
      const tp2Line = candlestickSeriesRef.current.createPriceLine({
        price: tp2,
        color: '#00C853',
        lineWidth: 1.5,
        lineStyle: 3,
        axisLabelVisible: true,
        title: `${titlePrefix}TP2: ${tp2.toFixed(decimals)}`,
      });
      priceLinesRef.current.push(tp2Line);
    }
  }, [confluenceData, positions, symbol]);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0E14] relative">
      {/* Top Chart Toolbar */}
      <div className="h-10 bg-[#151921] border-b border-[#222834] px-4 flex items-center justify-between select-none z-10">
        <div className="flex items-center space-x-3">
          <span className="font-bold font-mono text-sm text-white">{symbol}</span>
          <span className="text-xs text-gray-400">Institutional Chart</span>

          {/* Timeframe Switcher */}
          <div className="flex items-center space-x-1 pl-3 border-l border-[#222834]">
            {timeframes.map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange(tf)}
                className={`px-2 py-0.5 rounded text-xs font-mono font-medium transition ${
                  timeframe === tf
                    ? 'bg-[#00F0FF] text-black font-bold'
                    : 'text-gray-400 hover:text-white hover:bg-[#222834]'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs text-gray-400 font-mono">
          <span className="flex items-center space-x-1">
            <Layers className="w-3.5 h-3.5 text-[#00E676]" />
            <span>SMC Zones: ON</span>
          </span>
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div ref={chartContainerRef} className="flex-1 w-full h-full relative">
        {loading && (
          <div className="absolute inset-0 bg-[#0B0E14]/60 flex items-center justify-center z-20">
            <div className="flex items-center space-x-2 text-xs font-mono text-[#00F0FF]">
              <div className="w-4 h-4 border-2 border-[#00F0FF] border-t-transparent rounded-full animate-spin" />
              <span>STREAMING CANDLESTICK DATA...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

