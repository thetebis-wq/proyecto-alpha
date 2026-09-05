import React, { useState } from 'react';
import { StrategyKey, StrategyParams } from '../types';
import { RefreshCw, Send, Sliders, Shield, Bell, Cpu } from 'lucide-react';

export const COINS_MAP: Record<string, { id: string; symbol: string }> = {
  'Bitcoin (BTC)': { id: 'bitcoin', symbol: 'BTC' },
  'Ethereum (ETH)': { id: 'ethereum', symbol: 'ETH' },
  'Solana (SOL)': { id: 'solana', symbol: 'SOL' },
  'Binance Coin (BNB)': { id: 'binancecoin', symbol: 'BNB' },
  'Cardano (ADA)': { id: 'cardano', symbol: 'ADA' },
  'Ripple (XRP)': { id: 'ripple', symbol: 'XRP' },
};

interface SidebarProps {
  selectedCoinLabel: string;
  onSelectCoin: (label: string) => void;
  timeframeDays: number;
  onTimeframeChange: (days: number) => void;
  strategyKey: StrategyKey;
  onStrategyChange: (key: StrategyKey) => void;
  strategyParams: StrategyParams;
  onParamChange: (param: keyof StrategyParams, value: number) => void;
  feeRatePct: number;
  onFeeRateChange: (val: number) => void;
  enableSl: boolean;
  onToggleSl: (enabled: boolean) => void;
  slVal: number;
  onSlValChange: (val: number) => void;
  enableTp: boolean;
  onToggleTp: (enabled: boolean) => void;
  tpVal: number;
  onTpValChange: (val: number) => void;
  initialCapital: number;
  onInitialCapitalChange: (val: number) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  selectedCoinLabel,
  onSelectCoin,
  timeframeDays,
  onTimeframeChange,
  strategyKey,
  onStrategyChange,
  strategyParams,
  onParamChange,
  feeRatePct,
  onFeeRateChange,
  enableSl,
  onToggleSl,
  slVal,
  onSlValChange,
  enableTp,
  onToggleTp,
  tpVal,
  onTpValChange,
  initialCapital,
  onInitialCapitalChange,
  onRefresh,
  isRefreshing,
}) => {
  const [telegramStatus, setTelegramStatus] = useState<{
    loading: boolean;
    success?: boolean;
    msg?: string;
  }>({ loading: false });

  const handleTestTelegram = async () => {
    setTelegramStatus({ loading: true });
    try {
      const res = await fetch('/api/telegram/test', { method: 'POST' });
      const data = await res.json();
      if (res.ok && data.success) {
        setTelegramStatus({ loading: false, success: true, msg: '¡Mensaje enviado a tu Telegram!' });
      } else {
        setTelegramStatus({
          loading: false,
          success: false,
          msg: data.message || 'No se pudo enviar. Revisa tus credenciales en .env.',
        });
      }
    } catch (err: any) {
      setTelegramStatus({
        loading: false,
        success: false,
        msg: 'Error al contactar con el servidor local.',
      });
    }
    setTimeout(() => {
      setTelegramStatus((prev) => ({ ...prev, msg: undefined }));
    }, 6000);
  };

  const timeframeOptions = [7, 14, 30, 90, 180, 365];

  return (
    <aside className="w-full md:w-80 bg-[#161922] border-r border-[#262b3a] p-5 flex flex-col gap-6 text-sm overflow-y-auto shrink-0 min-h-screen">
      {/* 1. Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <h2 className="text-base font-semibold text-white tracking-wide">Parámetros de Mercado</h2>
        </div>
        <p className="text-xs text-gray-400">Configuración global del pipeline</p>
      </div>

      {/* 2. Coin Selector */}
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-medium text-gray-300">Criptoactivo:</label>
        <select
          id="coin-selector"
          value={selectedCoinLabel}
          onChange={(e) => onSelectCoin(e.target.value)}
          className="bg-[#212636] border border-[#30374e] rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
        >
          {Object.keys(COINS_MAP).map((coin) => (
            <option key={coin} value={coin}>
              {coin}
            </option>
          ))}
        </select>
      </div>

      {/* 3. Timeframe slider */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-center text-xs">
          <span className="font-medium text-gray-300">Historial (Días):</span>
          <span className="text-cyan-400 font-semibold">{timeframeDays} días</span>
        </div>
        <div className="grid grid-cols-6 gap-1">
          {timeframeOptions.map((days) => (
            <button
              key={days}
              id={`tf-btn-${days}`}
              type="button"
              onClick={() => onTimeframeChange(days)}
              className={`py-1 text-xs rounded font-medium transition-all ${
                timeframeDays === days
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'bg-[#212636] text-gray-400 hover:text-white hover:bg-[#2c3348]'
              }`}
            >
              {days}d
            </button>
          ))}
        </div>
      </div>

      <hr className="border-[#262b3a]" />

      {/* 4. Strategy Selector */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-white">Configuración de Estrategia</h3>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-gray-300">Estrategia Algorítmica:</label>
          <select
            id="strategy-selector"
            value={strategyKey}
            onChange={(e) => onStrategyChange(e.target.value as StrategyKey)}
            className="bg-[#212636] border border-[#30374e] rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
          >
            <option value="sma_crossover">Cruce de Medias (SMA Crossover)</option>
            <option value="mean_reversion">Reversión a la Media (Bollinger + RSI)</option>
          </select>
        </div>

        {/* Dynamic Params */}
        {strategyKey === 'sma_crossover' ? (
          <div className="grid grid-cols-2 gap-2 mt-1">
            <div>
              <label className="text-[11px] text-gray-400 block mb-1">SMA Rápida (h):</label>
              <input
                id="input-fast-sma"
                type="number"
                min={3}
                max={50}
                value={strategyParams.fast_period ?? 12}
                onChange={(e) => onParamChange('fast_period', parseInt(e.target.value, 10) || 12)}
                className="w-full bg-[#212636] border border-[#30374e] rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-[11px] text-gray-400 block mb-1">SMA Lenta (h):</label>
              <input
                id="input-slow-sma"
                type="number"
                min={10}
                max={120}
                value={strategyParams.slow_period ?? 24}
                onChange={(e) => onParamChange('slow_period', parseInt(e.target.value, 10) || 24)}
                className="w-full bg-[#212636] border border-[#30374e] rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3 mt-1">
            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Período Bollinger:</span>
                <span className="text-white font-medium">{strategyParams.bb_period ?? 20}</span>
              </div>
              <input
                id="slider-bb-period"
                type="range"
                min={10}
                max={50}
                value={strategyParams.bb_period ?? 20}
                onChange={(e) => onParamChange('bb_period', parseInt(e.target.value, 10))}
                className="w-full accent-cyan-500"
              />
            </div>
            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Umbral Sobreventa RSI:</span>
                <span className="text-emerald-400 font-medium">{strategyParams.rsi_oversold ?? 35}</span>
              </div>
              <input
                id="slider-rsi-oversold"
                type="range"
                min={15}
                max={45}
                value={strategyParams.rsi_oversold ?? 35}
                onChange={(e) => onParamChange('rsi_oversold', parseInt(e.target.value, 10))}
                className="w-full accent-emerald-500"
              />
            </div>
            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Umbral Sobrecompra RSI:</span>
                <span className="text-rose-400 font-medium">{strategyParams.rsi_overbought ?? 65}</span>
              </div>
              <input
                id="slider-rsi-overbought"
                type="range"
                min={55}
                max={85}
                value={strategyParams.rsi_overbought ?? 65}
                onChange={(e) => onParamChange('rsi_overbought', parseInt(e.target.value, 10))}
                className="w-full accent-rose-500"
              />
            </div>
          </div>
        )}
      </div>

      <hr className="border-[#262b3a]" />

      {/* 5. Risk & Friction Management */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Fricción y Gestión de Riesgo</h3>
        </div>

        <div>
          <label className="text-[11px] text-gray-400 block mb-1">
            Comisión de Exchange (%):
          </label>
          <input
            id="input-fee-rate"
            type="number"
            step="0.01"
            min="0"
            max="1.0"
            value={feeRatePct}
            onChange={(e) => onFeeRateChange(parseFloat(e.target.value) || 0)}
            className="w-full bg-[#212636] border border-[#30374e] rounded px-3 py-1.5 text-white text-xs focus:outline-none focus:border-cyan-500"
          />
          <span className="text-[10px] text-gray-500 mt-0.5 block">
            Comisión cobrada por orden (ej. 0.10% en Binance).
          </span>
        </div>

        {/* Stop Loss */}
        <div className="flex flex-col gap-1">
          <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
            <input
              id="check-sl"
              type="checkbox"
              checked={enableSl}
              onChange={(e) => onToggleSl(e.target.checked)}
              className="accent-cyan-500 rounded"
            />
            <span>Habilitar Stop-Loss</span>
          </label>
          {enableSl && (
            <div className="pl-5 pt-1">
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Stop-Loss (% Máx Caída):</span>
                <span className="text-rose-400 font-medium">-{slVal.toFixed(1)}%</span>
              </div>
              <input
                id="slider-sl-val"
                type="range"
                min={0.5}
                max={10.0}
                step={0.5}
                value={slVal}
                onChange={(e) => onSlValChange(parseFloat(e.target.value))}
                className="w-full accent-rose-500"
              />
            </div>
          )}
        </div>

        {/* Take Profit */}
        <div className="flex flex-col gap-1">
          <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
            <input
              id="check-tp"
              type="checkbox"
              checked={enableTp}
              onChange={(e) => onToggleTp(e.target.checked)}
              className="accent-cyan-500 rounded"
            />
            <span>Habilitar Take-Profit</span>
          </label>
          {enableTp && (
            <div className="pl-5 pt-1">
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Take-Profit (% Ganancia Objetivo):</span>
                <span className="text-emerald-400 font-medium">+{tpVal.toFixed(1)}%</span>
              </div>
              <input
                id="slider-tp-val"
                type="range"
                min={1.0}
                max={25.0}
                step={0.5}
                value={tpVal}
                onChange={(e) => onTpValChange(parseFloat(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>
          )}
        </div>

        <div>
          <label className="text-[11px] text-gray-400 block mb-1">
            Capital Inicial Simulado ($ USD):
          </label>
          <input
            id="input-initial-capital"
            type="number"
            min={500}
            max={1000000}
            step={1000}
            value={initialCapital}
            onChange={(e) => onInitialCapitalChange(parseFloat(e.target.value) || 10000)}
            className="w-full bg-[#212636] border border-[#30374e] rounded px-3 py-1.5 text-white text-xs focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* 6. Recalculate button */}
      <button
        id="btn-recalculate"
        type="button"
        onClick={onRefresh}
        disabled={isRefreshing}
        className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 text-white font-medium rounded-md shadow transition-colors disabled:opacity-50"
      >
        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        <span>Refrescar API y Recalcular</span>
      </button>

      <hr className="border-[#262b3a]" />

      {/* 7. Telegram Section */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-sky-400" />
          <h3 className="text-sm font-semibold text-white">Notificaciones Telegram</h3>
        </div>

        <button
          id="btn-test-telegram"
          type="button"
          onClick={handleTestTelegram}
          disabled={telegramStatus.loading}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-[#242c40] hover:bg-[#2d3750] text-sky-300 border border-sky-500/30 rounded-md font-medium text-xs transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
          <span>{telegramStatus.loading ? 'Enviando...' : '📲 Probar Alerta en Celular'}</span>
        </button>

        {telegramStatus.msg && (
          <div
            className={`p-2.5 rounded text-xs leading-relaxed ${
              telegramStatus.success
                ? 'bg-emerald-950/70 border border-emerald-600/40 text-emerald-300'
                : 'bg-rose-950/70 border border-rose-600/40 text-rose-300'
            }`}
          >
            {telegramStatus.msg}
          </div>
        )}
      </div>

      {/* Footer Caption */}
      <div className="mt-auto pt-4 text-center">
        <span className="text-[11px] text-gray-500 font-mono">
          ⚡ Proyecto Alpha v2.5 | Realismo Cuantitativo
        </span>
      </div>
    </aside>
  );
};
