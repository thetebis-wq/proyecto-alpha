import React, { useState } from 'react';
import { ProcessedMarketPoint } from '../types';
import { ChevronDown, ChevronUp, Download } from 'lucide-react';

interface DatasetExpanderProps {
  data: ProcessedMarketPoint[];
  coinId: string;
  timeframeDays: number;
}

export const DatasetExpander: React.FC<DatasetExpanderProps> = ({
  data,
  coinId,
  timeframeDays,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleDownloadCsv = () => {
    if (data.length === 0) return;

    const headers = [
      'timestamp',
      'dateStr',
      'price_usd',
      'volume_24h_usd',
      'market_cap_usd',
      'return_pct',
      'sma_dynamic',
      'rsi',
      'bb_upper',
      'bb_middle',
      'bb_lower',
      'macd_line',
      'macd_signal',
      'macd_hist',
      'position',
      'signal',
    ];

    const rows = data.map((d) =>
      headers
        .map((h) => {
          const val = (d as any)[h];
          if (val === undefined || val === null) return '';
          return typeof val === 'number' ? val.toFixed(4) : `"${val}"`;
        })
        .join(',')
    );

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${coinId}_${timeframeDays}d_quant_dataset.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const previewRows = data.slice(-30);

  return (
    <div className="bg-[#161922] border border-[#262b3a] rounded-lg overflow-hidden mt-6">
      <button
        id="btn-toggle-dataset"
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-xs font-semibold text-gray-200 hover:text-white hover:bg-[#1c212e] transition-colors"
      >
        <span className="flex items-center gap-2">
          <span>🔍 Explorar Datos Tabulares y Descargar Dataset Completo</span>
          <span className="text-gray-500 font-normal">({data.length} registros)</span>
        </span>
        {isOpen ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-[#262b3a] flex flex-col gap-4">
          <div className="overflow-x-auto max-h-[350px]">
            <table className="w-full text-left text-[11px] font-mono">
              <thead className="bg-[#1f2433] text-gray-400 uppercase text-[10px] sticky top-0 border-b border-[#262b3a]">
                <tr>
                  <th className="py-2 px-2.5">Fecha UTC</th>
                  <th className="py-2 px-2.5">Precio ($)</th>
                  <th className="py-2 px-2.5">Volumen ($)</th>
                  <th className="py-2 px-2.5">RSI (14)</th>
                  <th className="py-2 px-2.5">BB Superior</th>
                  <th className="py-2 px-2.5">BB Media</th>
                  <th className="py-2 px-2.5">BB Inferior</th>
                  <th className="py-2 px-2.5">MACD</th>
                  <th className="py-2 px-2.5">Posición</th>
                  <th className="py-2 px-2.5">Señal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#262b3a] text-gray-300">
                {previewRows.map((r, i) => (
                  <tr key={i} className="hover:bg-[#1a1f2e]">
                    <td className="py-1.5 px-2.5">{r.dateStr}</td>
                    <td className="py-1.5 px-2.5 font-medium text-white">${r.price_usd.toFixed(2)}</td>
                    <td className="py-1.5 px-2.5">${(r.volume_24h_usd / 1e6).toFixed(1)}M</td>
                    <td className="py-1.5 px-2.5">{r.rsi !== undefined ? r.rsi.toFixed(1) : '-'}</td>
                    <td className="py-1.5 px-2.5">{r.bb_upper !== undefined ? `$${r.bb_upper.toFixed(2)}` : '-'}</td>
                    <td className="py-1.5 px-2.5">{r.bb_middle !== undefined ? `$${r.bb_middle.toFixed(2)}` : '-'}</td>
                    <td className="py-1.5 px-2.5">{r.bb_lower !== undefined ? `$${r.bb_lower.toFixed(2)}` : '-'}</td>
                    <td className="py-1.5 px-2.5">{r.macd_line !== undefined ? r.macd_line.toFixed(2) : '-'}</td>
                    <td className="py-1.5 px-2.5">{r.position ?? 0}</td>
                    <td className="py-1.5 px-2.5 font-bold">
                      {r.signal === 1 ? (
                        <span className="text-emerald-400">+1 (Compra)</span>
                      ) : r.signal === -1 ? (
                        <span className="text-rose-400">-1 (Venta)</span>
                      ) : (
                        <span className="text-gray-500">0</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            id="btn-download-csv"
            type="button"
            onClick={handleDownloadCsv}
            className="self-start flex items-center gap-2 py-2 px-4 bg-[#232938] hover:bg-[#2c3447] text-white border border-[#39425a] rounded-md text-xs font-medium transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Descargar Dataset Cuantitativo ({coinId}_{timeframeDays}d_quant_dataset.csv)</span>
          </button>
        </div>
      )}
    </div>
  );
};
