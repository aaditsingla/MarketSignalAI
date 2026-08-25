import type { StockQuote } from "@/types/stock";
import type {
  StockHistory,
  StockHistoryPeriod,
} from "@/types/stockHistory";

export async function getApiHealth() {
  const response = await fetch("http://127.0.0.1:8000/health", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to connect to MarketSignal API");
  }

  return response.json();
}

export async function getStockQuote(symbol: string): Promise<StockQuote> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `http://127.0.0.1:8000/stocks/${normalizedSymbol}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(`Could not retrieve stock data for ${normalizedSymbol}`);
  }

  return response.json();
}

export async function getStockHistory(
  symbol: string,
  period: StockHistoryPeriod,
): Promise<StockHistory> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `http://127.0.0.1:8000/stocks/${normalizedSymbol}/history?period=${period}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Could not retrieve historical data for ${normalizedSymbol}`,
    );
  }

  return response.json();
}