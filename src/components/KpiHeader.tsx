import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface KpiHeaderProps {
  currentPrice: number;
  change24h: number;
  vol24h: number;
  minPeriod: number;
  maxPeriod: number;
}

export const KpiHeader: React.FC<KpiHeaderProps> = ({
  currentPrice,
  change24h,
  vol24h,
  minPeriod,
  maxPeriod,
}) => {
  const isPositive = change24h >= 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 my-6">
      {/* 1. Precio Spot */}
      <div id="kpi-spot-price" className="bg-[#161922] border border-[#262b3a] rounded-lg p-4 flex flex-col justify-between">
        <span className="text-xs font-medium text-gray-400">Precio Spot Actual</span>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-2xl font-bold text-white">
            ${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
        <div className={`flex items-center gap-1 text-xs font-semibold mt-2 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
          {isPositive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
          <span>{change24h >= 0 ? `+${change24h.toFixed(2)}%` : `${change24h.toFixed(2)}%`} (24h)</span>
        </div>
      </div>

      {/* 2. Volumen 24h */}
      <div id="kpi-volume-24h" className="bg-[#161922] border border-[#262b3a] rounded-lg p-4 flex flex-col justify-between">
        <span className="text-xs font-medium text-gray-400">Volumen 24 Horas</span>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-2xl font-bold text-white">
            ${(vol24h / 1e9).toFixed(2)} B
          </span>
        </div>
        <span className="text-[11px] text-gray-500 mt-2">Actividad global agregada</span>
      </div>

      {/* 3. Mínimo del Período */}
      <div id="kpi-min-period" className="bg-[#161922] border border-[#262b3a] rounded-lg p-4 flex flex-col justify-between">
        <span className="text-xs font-medium text-gray-400">Mínimo del Período</span>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-2xl font-bold text-gray-200">
            ${minPeriod.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
        <span className="text-[11px] text-gray-500 mt-2">Soporte técnico en el rango</span>
      </div>

      {/* 4. Máximo del Período */}
      <div id="kpi-max-period" className="bg-[#161922] border border-[#262b3a] rounded-lg p-4 flex flex-col justify-between">
        <span className="text-xs font-medium text-gray-400">Máximo del Período</span>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="text-2xl font-bold text-gray-200">
            ${maxPeriod.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
        <span className="text-[11px] text-gray-500 mt-2">Resistencia técnica en el rango</span>
      </div>
    </div>
  );
};
