import { ProcessedMarketPoint, StrategyKey, StrategyParams } from '../types';
import { TechnicalIndicators } from './technical_indicators';

export class StrategyEngine {
  static smaCrossover(
    data: ProcessedMarketPoint[],
    fastPeriod = 12,
    slowPeriod = 24
  ): ProcessedMarketPoint[] {
    const result = data.map((d) => ({ ...d }));
    const n = result.length;

    const fastSMAs: (number | undefined)[] = new Array(n);
    const slowSMAs: (number | undefined)[] = new Array(n);

    for (let i = 0; i < n; i++) {
      if (i >= fastPeriod - 1) {
        let sum = 0;
        for (let j = i - fastPeriod + 1; j <= i; j++) sum += result[j].price_usd;
        fastSMAs[i] = sum / fastPeriod;
      }
      if (i >= slowPeriod - 1) {
        let sum = 0;
        for (let j = i - slowPeriod + 1; j <= i; j++) sum += result[j].price_usd;
        slowSMAs[i] = sum / slowPeriod;
      }
      result[i].sma_fast = fastSMAs[i];
      result[i].sma_slow = slowSMAs[i];
      result[i].sma_dynamic = slowSMAs[i]; // Used by interactive market chart
    }

    let prevPos = 0;
    for (let i = 0; i < n; i++) {
      const fast = fastSMAs[i];
      const slow = slowSMAs[i];
      let pos = 0;
      if (fast !== undefined && slow !== undefined) {
        pos = fast > slow ? 1 : 0;
      }
      result[i].position = pos;
      result[i].signal = pos - prevPos;
      prevPos = pos;
    }

    return result;
  }

  static meanReversion(
    data: ProcessedMarketPoint[],
    bbPeriod = 20,
    rsiPeriod = 14,
    rsiOversold = 35.0,
    rsiOverbought = 65.0
  ): ProcessedMarketPoint[] {
    let result = TechnicalIndicators.addBollingerBands(data, bbPeriod, 2.0);
    result = TechnicalIndicators.addRSI(result, rsiPeriod);

    // Also populate sma_dynamic for plotting
    for (let i = 0; i < result.length; i++) {
      result[i].sma_dynamic = result[i].bb_middle;
    }

    const n = result.length;
    let currentPos = 0;
    let prevPos = 0;

    for (let i = 0; i < n; i++) {
      const p = result[i].price_usd;
      const lower = result[i].bb_lower;
      const middle = result[i].bb_middle;
      const rsi = result[i].rsi;

      if (lower === undefined || rsi === undefined || middle === undefined) {
        result[i].position = 0;
        result[i].signal = 0;
        continue;
      }

      if (currentPos === 0 && p <= lower && rsi <= rsiOversold) {
        currentPos = 1;
      } else if (currentPos === 1 && (p >= middle || rsi >= rsiOverbought)) {
        currentPos = 0;
      }

      result[i].position = currentPos;
      result[i].signal = currentPos - prevPos;
      prevPos = currentPos;
    }

    return result;
  }

  static applyStrategy(
    data: ProcessedMarketPoint[],
    strategy: StrategyKey,
    params: StrategyParams = {}
  ): ProcessedMarketPoint[] {
    if (strategy === 'sma_crossover') {
      const fast = params.fast_period ?? 12;
      const slow = params.slow_period ?? 24;
      return this.smaCrossover(data, fast, slow);
    }
    if (strategy === 'mean_reversion') {
      const bbP = params.bb_period ?? 20;
      const rsiP = params.rsi_period ?? 14;
      const rsiOs = params.rsi_oversold ?? 35.0;
      const rsiOb = params.rsi_overbought ?? 65.0;
      return this.meanReversion(data, bbP, rsiP, rsiOs, rsiOb);
    }
    return data;
  }
}
