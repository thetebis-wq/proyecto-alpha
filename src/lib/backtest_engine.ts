import { BacktestResult, ProcessedMarketPoint, TradeRecord } from '../types';

export class BacktestEngine {
  static runBacktest(
    data: ProcessedMarketPoint[],
    initialCapital = 10000.0,
    feeRate = 0.001,
    stopLossPct: number | null = 2.0,
    takeProfitPct: number | null = 5.0
  ): BacktestResult {
    if (data.length === 0) {
      return {
        initial_capital: initialCapital,
        final_capital: initialCapital,
        total_return_pct: 0,
        benchmark_return_pct: 0,
        max_drawdown_pct: 0,
        win_rate_pct: 0,
        profit_factor: 0,
        total_trades: 0,
        winning_trades: 0,
        losing_trades: 0,
        total_fees_paid: 0,
        stop_loss_count: 0,
        take_profit_count: 0,
        signal_exit_count: 0,
        equity_curve: [],
        benchmark_curve: [],
        drawdown_curve: [],
        trades: [],
      };
    }

    let capital = initialCapital;
    let positionUnits = 0.0;
    let inTrade = false;
    let entryPrice = 0.0;
    let entryDate = '';
    let tradeStartCapital = 0.0;
    let totalFeesPaid = 0.0;

    let stopLossCount = 0;
    let takeProfitCount = 0;
    let signalExitCount = 0;

    const trades: TradeRecord[] = [];
    const equityCurve: { dateStr: string; timestamp: number; equity: number }[] = [];
    const benchmarkCurve: { dateStr: string; timestamp: number; benchmark: number }[] = [];
    const drawdownCurve: { dateStr: string; timestamp: number; drawdown: number }[] = [];

    const initialPrice = data[0].price_usd;
    const benchmarkUnits = (initialCapital * (1.0 - feeRate)) / (initialPrice || 1);

    let cumMaxEquity = initialCapital;

    for (let i = 0; i < data.length; i++) {
      const point = data[i];
      const currentPrice = point.price_usd;
      const currentSignal = point.signal ?? 0;
      const isLastBar = i === data.length - 1;

      // 1. Exit Management if in trade
      if (inTrade) {
        const pnlUnrealizedPct = ((currentPrice - entryPrice) / entryPrice) * 100.0;
        let exitTriggered = false;
        let exitReason = '';

        if (stopLossPct !== null && pnlUnrealizedPct <= -Math.abs(stopLossPct)) {
          exitTriggered = true;
          exitReason = 'STOP_LOSS';
          stopLossCount++;
        } else if (takeProfitPct !== null && pnlUnrealizedPct >= Math.abs(takeProfitPct)) {
          exitTriggered = true;
          exitReason = 'TAKE_PROFIT';
          takeProfitCount++;
        } else if (currentSignal === -1) {
          exitTriggered = true;
          exitReason = 'SEÑAL_ESTRATEGIA';
          signalExitCount++;
        } else if (isLastBar) {
          exitTriggered = true;
          exitReason = 'FIN_PERIODO';
          signalExitCount++;
        }

        if (exitTriggered) {
          const grossSale = positionUnits * currentPrice;
          const exitFee = grossSale * feeRate;
          capital = grossSale - exitFee;
          totalFeesPaid += exitFee;

          const netTradePnlPct = ((capital - tradeStartCapital) / tradeStartCapital) * 100.0;
          const netTradePnlUsd = capital - tradeStartCapital;

          trades.push({
            entry_date: entryDate,
            exit_date: point.dateStr,
            entry_price: entryPrice,
            exit_price: currentPrice,
            exit_reason: exitReason,
            pnl_pct: netTradePnlPct,
            pnl_usd: netTradePnlUsd,
            won: netTradePnlPct > 0,
          });

          inTrade = false;
          positionUnits = 0.0;
        }
      }

      // 2. Entry Management if flat
      if (!inTrade && currentSignal === 1 && !isLastBar) {
        inTrade = true;
        entryDate = point.dateStr;
        entryPrice = currentPrice;
        tradeStartCapital = capital;

        const entryFee = capital * feeRate;
        totalFeesPaid += entryFee;
        const usableCapital = capital - entryFee;
        positionUnits = usableCapital / entryPrice;
      }

      // 3. Mark-to-market valuation
      const currentEquity = inTrade
        ? positionUnits * currentPrice * (1.0 - feeRate)
        : capital;

      equityCurve.push({
        dateStr: point.dateStr,
        timestamp: point.timestamp,
        equity: currentEquity,
      });

      const currentBenchmark = benchmarkUnits * currentPrice * (1.0 - feeRate);
      benchmarkCurve.push({
        dateStr: point.dateStr,
        timestamp: point.timestamp,
        benchmark: currentBenchmark,
      });

      cumMaxEquity = Math.max(cumMaxEquity, currentEquity);
      const currentDrawdown = ((currentEquity - cumMaxEquity) / cumMaxEquity) * 100.0;
      drawdownCurve.push({
        dateStr: point.dateStr,
        timestamp: point.timestamp,
        drawdown: currentDrawdown,
      });
    }

    const finalCapital = equityCurve[equityCurve.length - 1].equity;
    const totalReturnPct = ((finalCapital - initialCapital) / initialCapital) * 100.0;
    const finalBenchmark = benchmarkCurve[benchmarkCurve.length - 1].benchmark;
    const benchmarkReturnPct = ((finalBenchmark - initialCapital) / initialCapital) * 100.0;

    let minDrawdown = 0;
    for (const d of drawdownCurve) {
      if (d.drawdown < minDrawdown) minDrawdown = d.drawdown;
    }

    const totalTrades = trades.length;
    const winningTrades = trades.filter((t) => t.won);
    const losingTrades = trades.filter((t) => !t.won);

    const winRatePct = totalTrades > 0 ? (winningTrades.length / totalTrades) * 100.0 : 0.0;
    const totalGains = winningTrades.reduce((acc, t) => acc + t.pnl_usd, 0);
    const totalLosses = Math.abs(losingTrades.reduce((acc, t) => acc + t.pnl_usd, 0));
    const profitFactor =
      totalLosses > 0 ? totalGains / totalLosses : totalGains > 0 ? 99.9 : 0.0;

    return {
      initial_capital: initialCapital,
      final_capital: finalCapital,
      total_return_pct: totalReturnPct,
      benchmark_return_pct: benchmarkReturnPct,
      max_drawdown_pct: minDrawdown,
      win_rate_pct: winRatePct,
      profit_factor: profitFactor,
      total_trades: totalTrades,
      winning_trades: winningTrades.length,
      losing_trades: losingTrades.length,
      total_fees_paid: totalFeesPaid,
      stop_loss_count: stopLossCount,
      take_profit_count: takeProfitCount,
      signal_exit_count: signalExitCount,
      equity_curve: equityCurve,
      benchmark_curve: benchmarkCurve,
      drawdown_curve: drawdownCurve,
      trades,
    };
  }
}
