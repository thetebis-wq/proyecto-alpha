import { ProcessedMarketPoint } from '../types';

export class TechnicalIndicators {
  /**
   * Exponential Moving Average calculation.
   */
  static calcEMA(values: number[], span: number): number[] {
    const alpha = 2 / (span + 1);
    const ema: number[] = new Array(values.length);
    if (values.length === 0) return ema;

    ema[0] = values[0];
    for (let i = 1; i < values.length; i++) {
      ema[i] = values[i] * alpha + ema[i - 1] * (1 - alpha);
    }
    return ema;
  }

  /**
   * Calculates the Relative Strength Index (RSI) using Wilder's smoothing.
   */
  static addRSI(data: ProcessedMarketPoint[], period = 14): ProcessedMarketPoint[] {
    const n = data.length;
    if (n === 0) return [];

    const result = data.map((d) => ({ ...d }));
    const alpha = 1.0 / period;

    let avgGain = 0;
    let avgLoss = 0;

    // Initial period
    for (let i = 1; i < Math.min(period, n); i++) {
      const diff = result[i].price_usd - result[i - 1].price_usd;
      if (diff >= 0) avgGain += diff;
      else avgLoss += -diff;
    }
    avgGain /= period;
    avgLoss /= period;

    for (let i = 0; i < n; i++) {
      if (i < period) {
        result[i].rsi = undefined;
        continue;
      }

      const diff = result[i].price_usd - result[i - 1].price_usd;
      const gain = diff > 0 ? diff : 0;
      const loss = diff < 0 ? -diff : 0;

      avgGain = avgGain * (1 - alpha) + gain * alpha;
      avgLoss = avgLoss * (1 - alpha) + loss * alpha;

      if (avgLoss === 0) {
        result[i].rsi = 100.0;
      } else {
        const rs = avgGain / avgLoss;
        result[i].rsi = 100.0 - 100.0 / (1.0 + rs);
      }
    }

    return result;
  }

  /**
   * Calculates Bollinger Bands (middle, upper, lower, bandwidth).
   */
  static addBollingerBands(
    data: ProcessedMarketPoint[],
    period = 20,
    numStd = 2.0
  ): ProcessedMarketPoint[] {
    const result = data.map((d) => ({ ...d }));
    const n = result.length;

    for (let i = 0; i < n; i++) {
      if (i < period - 1) {
        result[i].bb_middle = undefined;
        result[i].bb_upper = undefined;
        result[i].bb_lower = undefined;
        result[i].bb_bandwidth = undefined;
        continue;
      }

      let sum = 0;
      for (let j = i - period + 1; j <= i; j++) {
        sum += result[j].price_usd;
      }
      const mean = sum / period;

      let varSum = 0;
      for (let j = i - period + 1; j <= i; j++) {
        varSum += Math.pow(result[j].price_usd - mean, 2);
      }
      const std = Math.sqrt(varSum / (period - 1 || 1));

      result[i].bb_middle = mean;
      result[i].bb_upper = mean + numStd * std;
      result[i].bb_lower = mean - numStd * std;
      result[i].bb_bandwidth = (result[i].bb_upper! - result[i].bb_lower!) / (mean || 1);
    }

    return result;
  }

  /**
   * Calculates MACD (line, signal, histogram).
   */
  static addMACD(
    data: ProcessedMarketPoint[],
    fastPeriod = 12,
    slowPeriod = 26,
    signalPeriod = 9
  ): ProcessedMarketPoint[] {
    const result = data.map((d) => ({ ...d }));
    const prices = result.map((d) => d.price_usd);

    const emaFast = this.calcEMA(prices, fastPeriod);
    const emaSlow = this.calcEMA(prices, slowPeriod);

    const macdLine: number[] = new Array(prices.length);
    for (let i = 0; i < prices.length; i++) {
      macdLine[i] = emaFast[i] - emaSlow[i];
    }

    const macdSignal = this.calcEMA(macdLine, signalPeriod);

    for (let i = 0; i < result.length; i++) {
      result[i].macd_line = macdLine[i];
      result[i].macd_signal = macdSignal[i];
      result[i].macd_hist = macdLine[i] - macdSignal[i];
    }

    return result;
  }

  /**
   * Applies all indicators to the series.
   */
  static addAllIndicators(data: ProcessedMarketPoint[]): ProcessedMarketPoint[] {
    let res = this.addRSI(data, 14);
    res = this.addBollingerBands(res, 20, 2.0);
    res = this.addMACD(res, 12, 26, 9);
    return res;
  }
}
