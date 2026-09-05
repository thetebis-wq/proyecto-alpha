import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { ProcessedMarketPoint } from '../types';

interface MarketTabProps {
  data: ProcessedMarketPoint[];
  assetName: string;
  smaPeriod: number;
}

export const MarketTab: React.FC<MarketTabProps> = ({ data, assetName, smaPeriod }) => {
  const [showBollinger, setShowBollinger] = useState(true);
  const [showSignals, setShowSignals] = useState(true);

  const formattedData = data.map((d) => ({
    ...d,
    time: d.dateStr,
    volB: d.volume_24h_usd ? d.volume_24h_usd / 1e9 : 0,
    buySignal: showSignals && d.signal === 1 ? d.price_usd : null,
    sellSignal: showSignals && d.signal === -1 ? d.price_usd : null,
  }));

  const minPrice = Math.min(...data.map((d) => d.price_usd)) * 0.98;
  const maxPrice = Math.max(...data.map((d) => d.price_usd)) * 1.02;

  return (
    <div className="flex flex-col gap-5">
      {/* Checkbox controls */}
      <div className="flex flex-wrap items-center gap-6 p-3 bg-[#161922] border border-[#262b3a] rounded-lg text-xs">
        <label className="flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white">
          <input
            id="check-show-bb"
            type="checkbox"
            checked={showBollinger}
            onChange={(e) => setShowBollinger(e.target.checked)}
            className="accent-cyan-500 rounded"
          />
          <span>Mostrar Bandas de Bollinger</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white">
          <input
            id="check-show-signals"
            type="checkbox"
            checked={showSignals}
            onChange={(e) => setShowSignals(e.target.checked)}
            className="accent-cyan-500 rounded"
          />
          <span>Mostrar Señales de Compra/Venta en Gráfico</span>
        </label>
      </div>

      {/* Main Market Structure Chart */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-semibold text-white">
            {assetName} – Análisis de Precio y Estructura
          </h4>
          <span className="text-xs text-gray-400">Escala USD</span>
        </div>

        <div className="h-[420px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={formattedData} margin={{ top: 10, right: 30, left: 15, bottom: 0 }}>
              <CartesianGrid stroke="#262b3a" strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="time"
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                minTickGap={40}
              />
              <YAxis
                domain={[minPrice, maxPrice]}
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickFormatter={(val) => `$${Number(val).toLocaleString()}`}
                orientation="right"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1e29',
                  borderColor: '#374151',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#fff',
                }}
                formatter={(value: any, name: string) => {
                  if (name === 'buySignal') return [`$${Number(value).toLocaleString()}`, '▲ COMPRA'];
                  if (name === 'sellSignal') return [`$${Number(value).toLocaleString()}`, '▼ VENTA'];
                  if (value === undefined || value === null) return ['N/A', name];
                  return [`$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />

              {/* Bollinger Upper & Lower bands */}
              {showBollinger && (
                <>
                  <Line
                    type="monotone"
                    dataKey="bb_upper"
                    name="Bollinger Sup"
                    stroke="#60a5fa"
                    strokeOpacity={0.4}
                    strokeWidth={1}
                    dot={false}
                    isAnimationActive={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="bb_lower"
                    name="Bollinger Inf"
                    stroke="#60a5fa"
                    strokeOpacity={0.4}
                    strokeWidth={1}
                    dot={false}
                    isAnimationActive={false}
                  />
                </>
              )}

              {/* Spot Price */}
              <Line
                type="monotone"
                dataKey="price_usd"
                name="Precio Spot (USD)"
                stroke="#00D4B2"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />

              {/* Dynamic SMA */}
              <Line
                type="monotone"
                dataKey="sma_dynamic"
                name={`SMA (${smaPeriod}h)`}
                stroke="#FFA500"
                strokeWidth={1.8}
                strokeDasharray="4 4"
                dot={false}
                isAnimationActive={false}
              />

              {/* Buy Signals */}
              {showSignals && (
                <Line
                  type="monotone"
                  dataKey="buySignal"
                  name="Señal COMPRA"
                  stroke="none"
                  dot={{ r: 6, fill: '#00FF7F', stroke: '#ffffff', strokeWidth: 1.5 }}
                  isAnimationActive={false}
                />
              )}

              {/* Sell Signals */}
              {showSignals && (
                <Line
                  type="monotone"
                  dataKey="sellSignal"
                  name="Señal VENTA"
                  stroke="none"
                  dot={{ r: 6, fill: '#FF4500', stroke: '#ffffff', strokeWidth: 1.5 }}
                  isAnimationActive={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Volume Chart */}
      <div className="bg-[#161922] border border-[#262b3a] rounded-lg p-4">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-semibold text-white">Volumen 24 Horas ($B)</h4>
        </div>
        <div className="h-[150px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={formattedData} margin={{ top: 5, right: 30, left: 15, bottom: 0 }}>
              <CartesianGrid stroke="#262b3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} minTickGap={40} />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                tickFormatter={(val) => `${Number(val).toFixed(1)}B`}
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
                formatter={(val: any) => [`$${Number(val).toFixed(2)} B`, 'Volumen 24h']}
              />
              <Bar dataKey="volB" name="Volumen ($B)" fill="#4A90E2" opacity={0.75} isAnimationActive={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
