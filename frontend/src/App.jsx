import React, { useState, useEffect, Component } from 'react';
import Header from './components/Header';
import WatchlistBar from './components/WatchlistBar';
import ChartView from './components/ChartView';
import ConfluenceRadar from './components/ConfluenceRadar';
import ExecutionDeck from './components/ExecutionDeck';
import EvolutionArena from './components/EvolutionArena';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-[#0B0E14] text-[#E6EDF3]">
          <h2 className="text-sm font-bold text-[#FF3B30] mb-2 font-mono">⚠️ View Rendering Interrupted</h2>
          <p className="text-xs text-gray-400 font-mono mb-4">{this.state.error?.message || 'Unexpected error'}</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="px-4 py-1.5 rounded bg-[#00F0FF] text-black font-bold text-xs font-mono"
          >
            RELOAD VIEW
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [activeView, setActiveView] = useState('terminal'); // 'terminal' or 'evolution'
  const [activeSymbol, setActiveSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('M15');

  const [status, setStatus] = useState(null);
  const [watchlist, setWatchlist] = useState([]);
  const [confluenceData, setConfluenceData] = useState(null);
  const [positions, setPositions] = useState({ open_positions: [] });
  const [wsConnected, setWsConnected] = useState(false);

  // Initial and periodic data fetch
  const fetchAllData = async () => {
    try {
      const [resStatus, resWatch, resConf, resPos] = await Promise.all([
        fetch('/api/status').then((r) => r.json()).catch(() => null),
        fetch('/api/watchlist').then((r) => r.json()).catch(() => null),
        fetch(`/api/confluence?symbol=${activeSymbol}`).then((r) => r.json()).catch(() => null),
        fetch('/api/positions').then((r) => r.json()).catch(() => null),
      ]);

      if (resStatus) setStatus(resStatus);
      if (resWatch && resWatch.watchlist) setWatchlist(resWatch.watchlist);
      if (resConf) setConfluenceData(resConf);
      if (resPos) setPositions(resPos);
    } catch (e) {
      console.error('Data fetch error:', e);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, [activeSymbol]);

  // WebSocket Live Stream Connection
  useEffect(() => {
    const wsUrl = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') +
      (window.location.host || '127.0.0.1:8000') + '/ws';

    let socket;
    const connect = () => {
      try {
        socket = new WebSocket(wsUrl);
        socket.onopen = () => setWsConnected(true);
        socket.onclose = () => {
          setWsConnected(false);
          setTimeout(connect, 3000); // Reconnect
        };
        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'TICK_UPDATE') {
              // Live update status PnL
              setStatus((prev) => ({
                ...(prev || {}),
                daily_pnl_usd: data.daily_pnl_usd,
                trades_taken_today: data.trades_count,
              }));
            }
          } catch (err) {}
        };
      } catch (err) {
        setWsConnected(false);
      }
    };

    connect();
    return () => {
      if (socket) socket.close();
    };
  }, []);

  // Execution Handlers
  const handleExecute = async (direction, riskPercent) => {
    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: activeSymbol,
          direction,
          risk_percent: riskPercent,
          account_balance: status?.account_balance || 10000.0,
        }),
      });
      const data = await res.json();
      fetchAllData();
    } catch (e) {
      console.error('Execute error:', e);
    }
  };

  const handleCloseAll = async () => {
    if (window.confirm('Emergency Killswitch: Are you sure you want to close ALL positions?')) {
      try {
        await fetch('/api/closeall', { method: 'POST' });
        fetchAllData();
      } catch (e) {
        console.error('Close all error:', e);
      }
    }
  };

  const handleSendTelegram = async () => {
    try {
      const res = await fetch('/api/telegram/alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: activeSymbol,
          direction: confluenceData?.confluence?.direction || 'BUY',
          include_chart: true,
        }),
      });
      const data = await res.json();
      alert(`Telegram Signal Dispatched! Status: ${data.status}`);
    } catch (e) {
      console.error('Telegram dispatch error:', e);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#0B0E14] text-[#E6EDF3] overflow-hidden">
      {/* Zone A: Top Header with Tab Switcher */}
      <Header
        activeView={activeView}
        onSwitchView={setActiveView}
        status={status}
        onOpenSettings={() => alert('Settings: Strategy DNA loaded from backend/config/strategy_dna.json')}
      />

      {/* View Switcher: Terminal View vs. Evolution Arena */}
      <ErrorBoundary>
        {activeView === 'evolution' ? (
          <EvolutionArena onBackToTerminal={() => setActiveView('terminal')} />
        ) : (
          <>
            {/* Main Work Area: Split into 3 columns (Zone B, C, D) */}
            <div className="flex-1 flex overflow-hidden">
              {/* Zone B: Left Watchlist */}
              <WatchlistBar
                watchlist={watchlist}
                activeSymbol={activeSymbol}
                onSelectSymbol={setActiveSymbol}
              />

              {/* Zone C: Center TradingView Interactive Chart */}
              <ChartView
                symbol={activeSymbol}
                timeframe={timeframe}
                onTimeframeChange={setTimeframe}
                confluenceData={confluenceData}
                positions={positions}
              />

              {/* Zone D: Right Confluence Radar */}
              <ConfluenceRadar confluenceData={confluenceData} />
            </div>

            {/* Zone E: Bottom Execution Control Deck */}
            <ExecutionDeck
              symbol={activeSymbol}
              status={status}
              positions={positions}
              onExecute={handleExecute}
              onCloseAll={handleCloseAll}
              onSendTelegramAlert={handleSendTelegram}
            />
          </>
        )}
      </ErrorBoundary>
    </div>
  );
}

