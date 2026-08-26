"use client";

import { useEffect, useState } from "react";

import {
  getStockQuote,
  getWatchlist,
  removeFromWatchlist,
} from "@/services/api";
import type { StockQuote } from "@/types/stock";
import type { WatchlistItem } from "@/types/watchlist";

interface WatchlistStock {
  item: WatchlistItem;
  quote: StockQuote | null;
}



async function fetchWatchlistStocks(): Promise<WatchlistStock[]> {
  const watchlist = await getWatchlist();

  return Promise.all(
    watchlist.map(async (item) => {
      try {
        const quote = await getStockQuote(item.symbol);

        return {
          item,
          quote,
        };
      } catch {
        return {
          item,
          quote: null,
        };
      }
    }),
  );
}

export default function Watchlist() {
  const [stocks, setStocks] = useState<WatchlistStock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadInitialWatchlist() {
      try {
        const watchlistStocks = await fetchWatchlistStocks();

        if (!cancelled) {
          setStocks(watchlistStocks);
          setError("");
        }
      } catch {
        if (!cancelled) {
          setError("Could not load watchlist.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadInitialWatchlist();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleRefresh() {
    try {
      setIsLoading(true);
      setError("");

      const watchlistStocks = await fetchWatchlistStocks();

      setStocks(watchlistStocks);
    } catch {
      setError("Could not load watchlist.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRemove(symbol: string) {
    try {
      await removeFromWatchlist(symbol);

      setStocks((currentStocks) =>
        currentStocks.filter(
          (stock) => stock.item.symbol !== symbol,
        ),
      );
    } catch {
      setError(`Could not remove ${symbol} from watchlist.`);
    }
  }

  return (
    <section className="mt-10">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Watchlist</h2>

        <button
          onClick={handleRefresh}
          className="rounded-lg border px-4 py-2 text-sm"
        >
          Refresh
        </button>
      </div>

      {isLoading && (
        <p className="mt-4 text-gray-500">
          Loading watchlist...
        </p>
      )}

      {error && (
        <p className="mt-4 text-red-500">
          {error}
        </p>
      )}

      {!isLoading && !error && stocks.length === 0 && (
        <p className="mt-4 text-gray-500">
          No stocks in your watchlist yet.
        </p>
      )}

      {!isLoading && stocks.length > 0 && (
        <div className="mt-5 grid gap-4">
          {stocks.map(({ item, quote }) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-xl border p-5"
            >
              <div>
                <p className="text-sm text-gray-500">
                  {item.symbol}
                </p>

                {quote ? (
                  <>
                    <p className="mt-1 font-semibold">
                      {quote.company_name}
                    </p>

                    <div className="mt-2 flex items-center gap-3">
                      <span className="text-xl font-bold">
                        {quote.currency} {quote.price.toFixed(2)}
                      </span>

                      <span
                        className={
                          quote.change >= 0
                            ? "text-green-500"
                            : "text-red-500"
                        }
                      >
                        {quote.change >= 0 ? "+" : ""}
                        {quote.change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="mt-1 text-gray-500">
                    Market data unavailable
                  </p>
                )}
              </div>

              <button
                onClick={() => handleRemove(item.symbol)}
                className="rounded-lg border px-4 py-2 text-sm text-red-500"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}