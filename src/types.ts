export interface RawMarketPoint {
  timestamp: number;
  price_usd: number;
  market_cap_usd: number;
  volume_24h_usd: number;
}

export interface ProcessedMarketPoint extends RawMarketPoint {
  dateStr: string;
  return_pct?: number;
  sma_24h?: number;
  sma_dynamic?: number;
  sma_fast?: number;
  sma_slow?: number;
  rsi?: number;
  bb_middle?: number;
  bb_upper?: number;
  bb_lower?: number;
  bb_bandwidth?: number;
  macd_line?: number;
  macd_signal?: number;
  macd_hist?: number;
  position?: number;
  signal?: number; // 1 = Buy, -1 = Sell, 0 = Hold
}

export type StrategyKey = 'sma_crossover' | 'mean_reversion';

export interface StrategyParams {
  fast_period?: number;
  slow_period?: number;
  bb_period?: number;
  rsi_period?: number;
  rsi_oversold?: number;
  rsi_overbought?: number;
}

export interface TradeRecord {
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  exit_reason: 'STOP_LOSS' | 'TAKE_PROFIT' | 'SEÑAL_ESTRATEGIA' | 'FIN_PERIODO' | string;
  pnl_pct: number;
  pnl_usd: number;
  won: boolean;
}

export interface BacktestResult {
  initial_capital: number;
  final_capital: number;
  total_return_pct: number;
  benchmark_return_pct: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  profit_factor: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  total_fees_paid: number;
  stop_loss_count: number;
  take_profit_count: number;
  signal_exit_count: number;
  equity_curve: { dateStr: string; timestamp: number; equity: number }[];
  benchmark_curve: { dateStr: string; timestamp: number; benchmark: number }[];
  drawdown_curve: { dateStr: string; timestamp: number; drawdown: number }[];
  trades: TradeRecord[];
}

export interface CoinSpotInfo {
  usd: number;
  usd_24h_change?: number;
  usd_24h_vol?: number;
}
