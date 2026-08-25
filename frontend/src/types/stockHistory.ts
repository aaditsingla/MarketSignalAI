export interface HistoricalPricePoint {
  timestamp: string;
  close: number;
}

export interface StockHistory {
  symbol: string;
  period: string;
  prices: HistoricalPricePoint[];
}

export type StockHistoryPeriod = "1d" | "1mo" | "6mo" | "1y";