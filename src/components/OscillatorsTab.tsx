import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine,
  Cell,
} from 'recharts';
import { ProcessedMarketPoint } from '../types';
import { Info } from 'lucide-react';

interface OscillatorsTabProps {
  data: ProcessedMarketPoint[];
}

export const OscillatorsTab: React.FC<OscillatorsTabProps> = ({ data }) => {
  const formattedData = data.map((d) => ({
    ...d,
    time: d.dateStr,
    histPositive: d.macd_hist !== undefined && d.macd_hist >= 0 ? d.macd_hist : 0,
    histNegative: d.macd_hist !== undefined && d.macd_hist < 0 ? d.macd_hist : 0,
  }));

  return (
    <div className="flex flex-col gap-5">
      {/* Informational banner */}
      <div className="flex items-start gap-3 p-4 bg-sky-950/40 border border-sky-800/40 rounded-lg text-xs text-sky-200 leading-relaxed">
        <Info className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-sky-300">💡 Interpretación Técnica: </span>
          <span>
            <b>RSI</b> indica Sobrecompra (&gt;70) o Sobreventa (&lt;30). <b>MACD</b> mide aceleración e inversión de tendencia mediante el cruce entre la línea rápida y la señal.
          </span>
        </div>
      </div>

      {/* 1. RSI Chart */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-semibold text-white">Índice de Fuerza Relativa (RSI 14)</h4>
          <span className="text-xs text-purple-400 font-mono">0 – 100</span>
        </div>

        <div className="h-[240px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={formattedData} margin={{ top: 10, right: 30, left: 15, bottom: 0 }}>
              <CartesianGrid stroke="#262b3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} minTickGap={40} />
              <YAxis domain={[0, 100]} stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} orientation="right" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1e29',
                  borderColor: '#374151',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: '#fff',
                }}
                formatter={(val: any) => [val !== undefined ? Number(val).toFixed(2) : 'N/A', 'RSI (14)']}
              />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Sobrecompra (70)', fill: '#ef4444', fontSize: 10, position: 'insideTopLeft' }} />
              <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Sobreventa (30)', fill: '#10b981', fontSize: 10, position: 'insideBottomLeft' }} />
              <Line
                type="monotone"
                dataKey="rsi"
                name="RSI (14)"
                stroke="#B388FF"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. MACD Chart */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-semibold text-white">MACD (12, 26, 9)</h4>
          <span className="text-xs text-cyan-400 font-mono">Momentum</span>
        </div>

        <div className="h-[260px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={formattedData} margin={{ top: 10, right: 30, left: 15, bottom: 0 }}>
              <CartesianGrid stroke="#262b3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} minTickGap={40} />
              <YAxis stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} orientation="right" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1e29',
                  borderColor: '#374151',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: '#fff',
                }}
                formatter={(val: any, name: string) => [val !== undefined ? Number(val).toFixed(2) : 'N/A', name]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />

              <Bar dataKey="macd_hist" name="Histograma" isAnimationActive={false}>
                {formattedData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={(entry.macd_hist ?? 0) >= 0 ? 'rgba(76, 175, 80, 0.75)' : 'rgba(244, 67, 54, 0.75)'}
                  />
                ))}
              </Bar>

              <Line
                type="monotone"
                dataKey="macd_line"
                name="Línea MACD"
                stroke="#29B6F6"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="macd_signal"
                name="Línea Señal"
                stroke="#FFA726"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
