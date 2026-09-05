import React, { useState, useEffect, useMemo } from 'react';
import { Sidebar, COINS_MAP } from './components/Sidebar';
import { KpiHeader } from './components/KpiHeader';
import { MarketTab } from './components/MarketTab';
import { OscillatorsTab } from './components/OscillatorsTab';
import { BacktestTab } from './components/BacktestTab';
import { DatasetExpander } from './components/DatasetExpander';
import {
  ProcessedMarketPoint,
  StrategyKey,
  StrategyParams,
  CoinSpotInfo,
} from './types';
import { TechnicalIndicators } from './lib/technical_indicators';
import { StrategyEngine } from './lib/strategies';
import { BacktestEngine } from './lib/backtest_engine';
import { BarChart3, Waves, Bot, AlertTriangle, RefreshCw } from 'lucide-react';

export function App() {
  const [selectedCoinLabel, setSelectedCoinLabel] = useState<string>('Bitcoin (BTC)');
  const [timeframeDays, setTimeframeDays] = useState<number>(30);
  const [strategyKey, setStrategyKey] = useState<StrategyKey>('sma_crossover');
  const [strategyParams, setStrategyParams] = useState<StrategyParams>({
    fast_period: 12,
    slow_period: 24,
    bb_period: 20,
    rsi_period: 14,
    rsi_oversold: 35,
    rsi_overbought: 65,
  });

  const [feeRatePct, setFeeRatePct] = useState<number>(0.1);
  const [enableSl, setEnableSl] = useState<boolean>(true);
  const [slVal, setSlVal] = useState<number>(2.0);
  const [enableTp, setEnableTp] = useState<boolean>(true);
  const [tpVal, setTpVal] = useState<number>(5.0);
  const [initialCapital, setInitialCapital] = useState<number>(10000.0);

  const [activeTab, setActiveTab] = useState<'market' | 'oscillators' | 'backtest'>('market');
  const [loading, setLoading] = useState<boolean>(true);
  const [rateLimited, setRateLimited] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [rawChart, setRawChart] = useState<{
    prices: [number, number][];
    market_caps: [number, number][];
    total_volumes: [number, number][];
  } | null>(null);

  const [spotInfo, setSpotInfo] = useState<CoinSpotInfo | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const coinId = useMemo(() => COINS_MAP[selectedCoinLabel]?.id || 'bitcoin', [selectedCoinLabel]);

  const handleParamChange = (param: keyof StrategyParams, value: number) => {
    setStrategyParams((prev) => ({ ...prev, [param]: value }));
  };

  // Fetch Data from Server API
  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      setLoading(true);
      setErrorMsg(null);
      setRateLimited(false);

      try {
        const [chartRes, spotRes] = await Promise.all([
          fetch(`/api/market-chart?coin_id=${coinId}&days=${timeframeDays}`),
          fetch(`/api/spot-price?coin_id=${coinId}`),
        ]);

        if (!isCancelled) {
          if (chartRes.ok) {
            const chartJson = await chartRes.json();
            if (chartJson.rate_limited) {
              setRateLimited(true);
            }
            setRawChart({
              prices: chartJson.prices || [],
              market_caps: chartJson.market_caps || [],
              total_volumes: chartJson.total_volumes || [],
            });
          }

          if (spotRes.ok) {
            const spotJson = await spotRes.json();
            const coinData = spotJson[coinId];
            if (coinData) {
              setSpotInfo({
                usd: coinData.usd,
                usd_24h_change: coinData.usd_24h_change ?? 0,
                usd_24h_vol: coinData.usd_24h_vol ?? 0,
              });
            }
          }
        }
      } catch (err: any) {
        if (!isCancelled) {
          setErrorMsg(err.message || 'Error de conectividad al cargar datos de mercado.');
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      isCancelled = true;
    };
  }, [coinId, timeframeDays, refreshTrigger]);

  // Transform raw data into time series and calculate indicators
  const processedData = useMemo(() => {
    if (!rawChart || !rawChart.prices || rawChart.prices.length === 0) return [];

    const volumeMap = new Map<number, number>();
    const capMap = new Map<number, number>();

    for (const [t, v] of rawChart.total_volumes || []) {
      volumeMap.set(t, v);
    }
    for (const [t, c] of rawChart.market_caps || []) {
      capMap.set(t, c);
    }

    // Convert raw points
    const points: ProcessedMarketPoint[] = rawChart.prices.map(([timestamp, price]) => {
      const d = new Date(timestamp);
      const dateStr = d.toISOString().replace('T', ' ').slice(0, 16);
      return {
        timestamp,
        dateStr,
        price_usd: price,
        volume_24h_usd: volumeMap.get(timestamp) ?? 0,
        market_cap_usd: capMap.get(timestamp) ?? 0,
      };
    });

    // Add returns
    for (let i = 1; i < points.length; i++) {
      const prevP = points[i - 1].price_usd;
      points[i].return_pct = prevP > 0 ? (points[i].price_usd - prevP) / prevP : 0;
    }

    // 1. Add all base indicators (RSI, Bollinger, MACD)
    const withIndicators = TechnicalIndicators.addAllIndicators(points);

    // 2. Apply chosen algorithmic strategy
    const withSignals = StrategyEngine.applyStrategy(withIndicators, strategyKey, strategyParams);

    return withSignals;
  }, [rawChart, strategyKey, strategyParams]);

  // Execute Backtest
  const backtestResult = useMemo(() => {
    const feeRate = feeRatePct / 100.0;
    const sl = enableSl ? slVal : null;
    const tp = enableTp ? tpVal : null;

    return BacktestEngine.runBacktest(processedData, initialCapital, feeRate, sl, tp);
  }, [processedData, initialCapital, feeRatePct, enableSl, slVal, enableTp, tpVal]);

  // Derived KPI values
  const currentPrice = useMemo(() => {
    if (spotInfo?.usd) return spotInfo.usd;
    if (processedData.length > 0) return processedData[processedData.length - 1].price_usd;
    return 0;
  }, [spotInfo, processedData]);

  const change24h = spotInfo?.usd_24h_change ?? 0;
  const vol24h = spotInfo?.usd_24h_vol ?? (processedData[processedData.length - 1]?.volume_24h_usd || 0);

  const minPeriodPrice = useMemo(() => {
    if (processedData.length === 0) return 0;
    return Math.min(...processedData.map((d) => d.price_usd));
  }, [processedData]);

  const maxPeriodPrice = useMemo(() => {
    if (processedData.length === 0) return 0;
    return Math.max(...processedData.map((d) => d.price_usd));
  }, [processedData]);

  const strategyNameMap: Record<StrategyKey, string> = {
    sma_crossover: 'Cruce de Medias (SMA Crossover)',
    mean_reversion: 'Reversión a la Media (Bollinger + RSI)',
  };

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-[#0e1117] text-[#f0f2f6]">
      {/* 1. Left Sidebar */}
      <Sidebar
        selectedCoinLabel={selectedCoinLabel}
        onSelectCoin={setSelectedCoinLabel}
        timeframeDays={timeframeDays}
        onTimeframeChange={setTimeframeDays}
        strategyKey={strategyKey}
        onStrategyChange={setStrategyKey}
        strategyParams={strategyParams}
        onParamChange={handleParamChange}
        feeRatePct={feeRatePct}
        onFeeRateChange={setFeeRatePct}
        enableSl={enableSl}
        onToggleSl={setEnableSl}
        slVal={slVal}
        onSlValChange={setSlVal}
        enableTp={enableTp}
        onToggleTp={setEnableTp}
        tpVal={tpVal}
        onTpValChange={setTpVal}
        initialCapital={initialCapital}
        onInitialCapitalChange={setInitialCapital}
        onRefresh={() => setRefreshTrigger((prev) => prev + 1)}
        isRefreshing={loading}
      />

      {/* 2. Main Content Area */}
      <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full overflow-x-hidden">
        {/* Header Title */}
        <header className="mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Proyecto Alpha – Terminal Cuantitativa
            </h1>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            Análisis y simulación algorítmica para <span className="font-semibold text-cyan-400">{selectedCoinLabel}</span> en dólares estadounidenses.
          </p>
        </header>

        {/* Rate Limit Warning Notification */}
        {rateLimited && (
          <div className="mb-4 p-3.5 bg-amber-950/60 border border-amber-500/50 rounded-lg text-amber-200 text-xs flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-semibold block mb-0.5">⚠️ Límite de Peticiones de CoinGecko Alcanzado (HTTP 429)</span>
              <span>
                Has superado el límite temporal de consultas por minuto de la API pública de CoinGecko. Los datos cacheados y de respaldo protegen el sistema cuantitativo.
              </span>
            </div>
            <button
              type="button"
              onClick={() => setRefreshTrigger((prev) => prev + 1)}
              className="px-2.5 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium text-xs whitespace-nowrap"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Error message if any */}
        {errorMsg && (
          <div className="mb-4 p-3 bg-rose-950/60 border border-rose-500/50 rounded-lg text-rose-200 text-xs flex items-center justify-between">
            <span>❌ {errorMsg}</span>
            <button
              type="button"
              onClick={() => setRefreshTrigger((prev) => prev + 1)}
              className="px-2 py-0.5 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Loading Spinner State */}
        {loading && (
          <div className="my-3 py-2 px-3 bg-[#161922] border border-cyan-500/30 rounded-md text-cyan-300 text-xs flex items-center gap-2">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            <span>Descargando mercado y ejecutando simulación...</span>
          </div>
        )}

        {/* Live KPI Cards Header */}
        <KpiHeader
          currentPrice={currentPrice}
          change24h={change24h}
          vol24h={vol24h}
          minPeriod={minPeriodPrice}
          maxPeriod={maxPeriodPrice}
        />

        <hr className="border-[#262b3a] my-6" />

        {/* Main Tab Navigation */}
        <div className="flex border-b border-[#262b3a] mb-6 gap-2">
          <button
            id="tab-market"
            type="button"
            onClick={() => setActiveTab('market')}
            className={`flex items-center gap-2 py-2.5 px-4 text-xs font-semibold rounded-t-lg transition-all border-b-2 ${
              activeTab === 'market'
                ? 'border-cyan-400 text-cyan-300 bg-[#161922]'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-[#161922]/50'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>📊 Análisis de Mercado & Señales</span>
          </button>

          <button
            id="tab-oscillators"
            type="button"
            onClick={() => setActiveTab('oscillators')}
            className={`flex items-center gap-2 py-2.5 px-4 text-xs font-semibold rounded-t-lg transition-all border-b-2 ${
              activeTab === 'oscillators'
                ? 'border-cyan-400 text-cyan-300 bg-[#161922]'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-[#161922]/50'
            }`}
          >
            <Waves className="w-3.5 h-3.5" />
            <span>🌊 Osciladores (RSI & MACD)</span>
          </button>

          <button
            id="tab-backtest"
            type="button"
            onClick={() => setActiveTab('backtest')}
            className={`flex items-center gap-2 py-2.5 px-4 text-xs font-semibold rounded-t-lg transition-all border-b-2 ${
              activeTab === 'backtest'
                ? 'border-cyan-400 text-cyan-300 bg-[#161922]'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-[#161922]/50'
            }`}
          >
            <Bot className="w-3.5 h-3.5" />
            <span>🤖 Laboratorio de Backtesting</span>
          </button>
        </div>

        {/* Tab Content Display */}
        {activeTab === 'market' && (
          <MarketTab
            data={processedData}
            assetName={selectedCoinLabel}
            smaPeriod={strategyParams.slow_period ?? 24}
          />
        )}

        {activeTab === 'oscillators' && (
          <OscillatorsTab data={processedData} />
        )}

        {activeTab === 'backtest' && (
          <BacktestTab
            result={backtestResult}
            strategyLabel={strategyNameMap[strategyKey]}
            feeRatePct={feeRatePct}
          />
        )}

        {/* Tabular Data Explorer & CSV Export */}
        <DatasetExpander
          data={processedData}
          coinId={coinId}
          timeframeDays={timeframeDays}
        />
      </main>
    </div>
  );
}

export default App;
