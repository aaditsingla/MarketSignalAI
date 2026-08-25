export interface StockQuote {
  symbol: string;
  company_name: string;
  price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  market_cap: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  currency: string;
}