import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { BacktestResult } from '../types';
import { TrendingUp, TrendingDown, Target, AlertTriangle, Scale } from 'lucide-react';

interface BacktestTabProps {
  result: BacktestResult;
  strategyLabel: string;
  feeRatePct: number;
}

export const BacktestTab: React.FC<BacktestTabProps> = ({
  result,
  strategyLabel,
  feeRatePct,
}) => {
  const chartData = result.equity_curve.map((point, idx) => ({
    time: point.dateStr,
    equity: point.equity,
    benchmark: result.benchmark_curve[idx]?.benchmark ?? point.equity,
    drawdown: result.drawdown_curve[idx]?.drawdown ?? 0,
  }));

  const netGain = result.final_capital - result.initial_capital;
  const isStrategyPositive = result.total_return_pct >= 0;

  const reasonMap: Record<string, string> = {
    STOP_LOSS: '🛑 Stop-Loss',
    TAKE_PROFIT: '🎯 Take-Profit',
    SEÑAL_ESTRATEGIA: '🔄 Señal',
    FIN_PERIODO: '⏳ Fin Período',
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h3 className="text-base font-semibold text-white">
          Resultados de Simulación: <span className="text-cyan-400">{strategyLabel}</span>
        </h3>
        <p className="text-xs text-gray-400 mt-0.5">
          Contabilidad neta mark-to-market con comisiones y corte de riesgo
        </p>
      </div>

      {/* Row 1: 5 Core Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        <div id="metric-strat-return" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3 flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-400">Retorno Neto Estrategia</span>
          <span className={`text-xl font-bold mt-1 ${isStrategyPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {result.total_return_pct >= 0 ? `+${result.total_return_pct.toFixed(2)}%` : `${result.total_return_pct.toFixed(2)}%`}
          </span>
          <span className={`text-[11px] font-medium mt-1 ${netGain >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {netGain >= 0 ? `+$${netGain.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : `-$${Math.abs(netGain).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          </span>
        </div>

        <div id="metric-benchmark" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3 flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-400">Buy & Hold (Benchmark)</span>
          <span className={`text-xl font-bold mt-1 ${result.benchmark_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {result.benchmark_return_pct >= 0 ? `+${result.benchmark_return_pct.toFixed(2)}%` : `${result.benchmark_return_pct.toFixed(2)}%`}
          </span>
          <span className="text-[11px] text-gray-500 mt-1">Rendimiento pasivo spot</span>
        </div>

        <div id="metric-win-rate" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3 flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-400">Win Rate (% Aciertos)</span>
          <span className="text-xl font-bold text-white mt-1">
            {result.win_rate_pct.toFixed(1)}%
          </span>
          <span className="text-[11px] text-gray-400 mt-1">
            {result.winning_trades} ganadores de {result.total_trades} trades
          </span>
        </div>

        <div id="metric-max-drawdown" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3 flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-400">Máximo Drawdown (Riesgo)</span>
          <span className="text-xl font-bold text-rose-400 mt-1">
            {result.max_drawdown_pct.toFixed(2)}%
          </span>
          <span className="text-[11px] text-gray-500 mt-1">Caída máxima desde pico</span>
        </div>

        <div id="metric-profit-factor" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3 flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-400">Profit Factor</span>
          <span className="text-xl font-bold text-cyan-400 mt-1">
            {result.profit_factor.toFixed(2)}
          </span>
          <span className="text-[11px] text-gray-500 mt-1">Ganancias brutas / pérdidas</span>
        </div>
      </div>

      {/* Row 2: 4 Friction & Risk Breakdown Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div id="metric-fees-paid" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3">
          <span className="text-[11px] text-gray-400">Comisiones Pagadas</span>
          <div className="text-lg font-bold text-amber-300 mt-0.5">
            ${result.total_fees_paid.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-[10px] text-gray-500">Tasa: {feeRatePct.toFixed(2)}% por orden</span>
        </div>

        <div id="metric-sl-exits" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3">
          <span className="text-[11px] text-gray-400">Salidas por Stop-Loss</span>
          <div className="text-lg font-bold text-rose-400 mt-0.5">
            {result.stop_loss_count} trades
          </div>
          <span className="text-[10px] text-gray-500">Límite de pérdida de emergencia</span>
        </div>

        <div id="metric-tp-exits" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3">
          <span className="text-[11px] text-gray-400">Salidas por Take-Profit</span>
          <div className="text-lg font-bold text-emerald-400 mt-0.5">
            {result.take_profit_count} trades
          </div>
          <span className="text-[10px] text-gray-500">Objetivo de ganancia alcanzado</span>
        </div>

        <div id="metric-signal-exits" className="bg-[#161922] border border-[#262b3a] rounded-lg p-3">
          <span className="text-[11px] text-gray-400">Salidas por Señal Técnica</span>
          <div className="text-lg font-bold text-sky-400 mt-0.5">
            {result.signal_exit_count} trades
          </div>
          <span className="text-[10px] text-gray-500">Inversión o fin de rango</span>
        </div>
      </div>

      {/* Equity Curve Chart */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-semibold text-white">Curva de Capital (Estrategia vs Buy & Hold)</h4>
          <span className="text-xs text-gray-400">Base ${result.initial_capital.toLocaleString()}</span>
        </div>

        <div className="h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 15, bottom: 0 }}>
              <CartesianGrid stroke="#262b3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} minTickGap={40} />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                tickFormatter={(val) => `$${Number(val).toLocaleString()}`}
                orientation="right"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1e29',
                  borderColor: '#374151',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: '#fff',
                }}
                formatter={(val: any, name: string) => [`$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, name]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />
              <Line
                type="monotone"
                dataKey="equity"
                name="Estrategia Algorítmica"
                stroke="#00E676"
                strokeWidth={2.2}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="benchmark"
                name="Buy & Hold (Benchmark)"
                stroke="#78909C"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Underwater Drawdown Chart */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-semibold text-white">Underwater Chart (Drawdown %)</h4>
          <span className="text-xs text-rose-400 font-mono">
            Pérdida máxima: {result.max_drawdown_pct.toFixed(2)}%
          </span>
        </div>

        <div className="h-[160px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 15, bottom: 0 }}>
              <CartesianGrid stroke="#262b3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} minTickGap={40} />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                tickFormatter={(val) => `${Number(val).toFixed(1)}%`}
                orientation="right"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1e29',
                  borderColor: '#374151',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: '#fff',
                }}
                formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Drawdown']}
              />
              <Area
                type="monotone"
                dataKey="drawdown"
                name="Drawdown"
                stroke="#EF5350"
                fill="#EF5350"
                fillOpacity={0.25}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Trades Table */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <h4 className="text-sm font-semibold text-white mb-3">
          📋 Historial de Operaciones Detallado ({result.total_trades} trades)
        </h4>

        {result.trades.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#1f2433] text-gray-400 uppercase text-[10px] tracking-wider border-b border-[#262b3a]">
                <tr>
                  <th className="py-2.5 px-3">Fecha Entrada</th>
                  <th className="py-2.5 px-3">Fecha Salida</th>
                  <th className="py-2.5 px-3">Precio Entrada</th>
                  <th className="py-2.5 px-3">Precio Salida</th>
                  <th className="py-2.5 px-3">Motivo Salida</th>
                  <th className="py-2.5 px-3">Rendimiento Neto (%)</th>
                  <th className="py-2.5 px-3">Ganancia/Pérdida ($)</th>
                  <th className="py-2.5 px-3 text-center">¿Ganador?</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#262b3a]">
                {result.trades.map((t, i) => {
                  const won = t.won;
                  return (
                    <tr key={i} className="hover:bg-[#1a1f2e] transition-colors">
                      <td className="py-2 px-3 text-gray-300 font-mono text-[11px]">{t.entry_date}</td>
                      <td className="py-2 px-3 text-gray-300 font-mono text-[11px]">{t.exit_date}</td>
                      <td className="py-2 px-3 text-white font-medium">${t.entry_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                      <td className="py-2 px-3 text-white font-medium">${t.exit_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                      <td className="py-2 px-3">
                        <span className="px-2 py-0.5 rounded bg-[#252b3d] text-[10px] font-medium text-gray-300 border border-[#373f57]">
                          {reasonMap[t.exit_reason] || t.exit_reason}
                        </span>
                      </td>
                      <td className={`py-2 px-3 font-semibold ${won ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {t.pnl_pct >= 0 ? `+${t.pnl_pct.toFixed(2)}%` : `${t.pnl_pct.toFixed(2)}%`}
                      </td>
                      <td className={`py-2 px-3 font-semibold ${won ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {t.pnl_usd >= 0 ? `+$${t.pnl_usd.toFixed(2)}` : `-$${Math.abs(t.pnl_usd).toFixed(2)}`}
                      </td>
                      <td className="py-2 px-3 text-center">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${won ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}`}>
                          {won ? 'SÍ' : 'NO'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-4 bg-[#1a1e29] rounded text-xs text-gray-400 text-center">
            No se generaron trades con los parámetros actuales en este rango temporal.
          </div>
        )}
      </div>
    </div>
  );
};
