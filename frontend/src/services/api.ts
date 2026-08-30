import type { MarketAnalysisResult } from "@/types/analysis";
import type { StockQuote } from "@/types/stock";
import type {
  StockHistory,
  StockHistoryPeriod,
} from "@/types/stockHistory";
import type { WatchlistItem } from "@/types/watchlist";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function getApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to connect to MarketSignal API");
  }

  return response.json();
}

export async function getStockQuote(
  symbol: string,
): Promise<StockQuote> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `${API_BASE_URL}/stocks/${normalizedSymbol}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Could not retrieve stock data for ${normalizedSymbol}`,
    );
  }

  return response.json();
}

export async function getStockHistory(
  symbol: string,
  period: StockHistoryPeriod,
): Promise<StockHistory> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `${API_BASE_URL}/stocks/${normalizedSymbol}/history?period=${period}`,
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

export async function getWatchlist(): Promise<WatchlistItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/watchlist`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error("Could not retrieve watchlist");
  }

  return response.json();
}

export async function addToWatchlist(
  symbol: string,
): Promise<WatchlistItem> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `${API_BASE_URL}/watchlist/${normalizedSymbol}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Could not add ${normalizedSymbol} to watchlist`,
    );
  }

  return response.json();
}

export async function removeFromWatchlist(
  symbol: string,
): Promise<void> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `${API_BASE_URL}/watchlist/${normalizedSymbol}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Could not remove ${normalizedSymbol} from watchlist`,
    );
  }
}

export async function runMarketAnalysis(
  symbol: string,
): Promise<MarketAnalysisResult> {
  const normalizedSymbol = symbol.trim().toUpperCase();

  const response = await fetch(
    `${API_BASE_URL}/analysis/${normalizedSymbol}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    let errorMessage = (
      `Could not analyze ${normalizedSymbol}`
    );

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(errorMessage);
  }

  return response.json();
}