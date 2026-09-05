import { RawMarketPoint } from '../types';

export const BASE_PRICES: Record<string, { price: number; vol: number }> = {
  bitcoin: { price: 68450, vol: 32.5e9 },
  ethereum: { price: 3520, vol: 18.2e9 },
  solana: { price: 148.5, vol: 4.8e9 },
  binancecoin: { price: 585.0, vol: 1.2e9 },
  cardano: { price: 0.48, vol: 0.55e9 },
  ripple: { price: 0.59, vol: 1.1e9 },
};

/**
 * Generates realistic deterministic historical price series for fallback/demo.
 */
export function generateMockMarketChart(coinId: string, days = 30): {
  prices: [number, number][];
  market_caps: [number, number][];
  total_volumes: [number, number][];
} {
  const base = BASE_PRICES[coinId] || { price: 100, vol: 1e9 };
  const now = Date.now();
  // Points: hourly for <= 30 days (e.g. 24*days), or every 4 hours for > 30 days
  const stepHours = days <= 14 ? 1 : days <= 90 ? 4 : 24;
  const totalSteps = Math.min(Math.floor((days * 24) / stepHours), 500);
  const stepMs = (days * 86400000) / totalSteps;

  const prices: [number, number][] = [];
  const market_caps: [number, number][] = [];
  const total_volumes: [number, number][] = [];

  let currentPrice = base.price * (1 - (Math.sin(days) * 0.15));

  for (let i = 0; i <= totalSteps; i++) {
    const time = now - (totalSteps - i) * stepMs;
    // Deterministic cyclical movement + trend
    const cycle = Math.sin((i / 15) * Math.PI) * 0.02 + Math.cos((i / 35) * Math.PI) * 0.035;
    const drift = (i / totalSteps - 0.5) * 0.05;
    const noise = Math.sin(i * 997.1) * 0.012;
    currentPrice = Math.max(currentPrice * (1 + cycle * 0.2 + drift * 0.05 + noise), base.price * 0.2);

    prices.push([time, currentPrice]);
    market_caps.push([time, currentPrice * 1.9e7]);
    total_volumes.push([time, base.vol * (0.8 + Math.abs(Math.sin(i * 1.3)) * 0.4)]);
  }

  return { prices, market_caps, total_volumes };
}
