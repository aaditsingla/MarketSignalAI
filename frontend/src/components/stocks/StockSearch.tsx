"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import StockCard from "@/components/stocks/StockCard";
import {
  addToWatchlist,
  getStockQuote,
} from "@/services/api";
import type { StockQuote } from "@/types/stock";

interface StockSearchProps {
  onWatchlistChanged: () => void;
}

export default function StockSearch({
  onWatchlistChanged,
}: StockSearchProps) {
  const [symbol, setSymbol] = useState("");
  const [stock, setStock] =
    useState<StockQuote | null>(null);

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] =
    useState(false);

  const [isAdding, setIsAdding] =
    useState(false);

  const [
    watchlistMessage,
    setWatchlistMessage,
  ] = useState("");

  const activeSymbol = stock?.symbol ?? null;

  useEffect(() => {
    if (!activeSymbol) {
      return;
    }

    const intervalId = window.setInterval(
      async () => {
        try {
          const refreshedStock =
            await getStockQuote(activeSymbol);

          setStock(refreshedStock);
        } catch {
          // Keep the last successful quote.
        }
      },
      60000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [activeSymbol]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const trimmedSymbol = symbol.trim();

    if (!trimmedSymbol) {
      setError("Enter a stock symbol.");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      setWatchlistMessage("");

      const stockData =
        await getStockQuote(trimmedSymbol);

      setStock(stockData);
    } catch {
      setStock(null);

      setError(
        `Could not find stock data for ${trimmedSymbol.toUpperCase()}.`,
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAddToWatchlist(
    stockSymbol: string,
  ) {
    try {
      setIsAdding(true);
      setWatchlistMessage("");

      await addToWatchlist(stockSymbol);

      onWatchlistChanged();

      setWatchlistMessage(
        `${stockSymbol} added to your watchlist.`,
      );
    } catch {
      setWatchlistMessage(
        `${stockSymbol} is already in your watchlist or could not be added.`,
      );
    } finally {
      setIsAdding(false);
    }
  }

  return (
    <section className="mt-12">
      <div className="rounded-2xl border border-gray-800 bg-gray-950/30 p-5 md:p-6">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
            Stock Research
          </p>

          <h2 className="mt-2 text-2xl font-bold">
            Research a company
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500">
            Search by ticker to view current market
            data, price history, and run a full
            MarketSignal news analysis.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="mt-5 flex max-w-2xl flex-col gap-3 sm:flex-row"
        >
          <input
            type="text"
            value={symbol}
            onChange={(event) =>
              setSymbol(event.target.value)
            }
            placeholder="Search ticker, e.g. NVDA"
            className="min-w-0 flex-1 rounded-xl border border-gray-700 bg-black/30 px-4 py-3 text-gray-100 outline-none transition placeholder:text-gray-600 focus:border-gray-500"
          />

          <button
            type="submit"
            disabled={isLoading}
            className="rounded-xl bg-white px-6 py-3 font-semibold text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading
              ? "Searching..."
              : "Search Stock"}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
            {error}
          </div>
        )}
      </div>

      {stock && (
        <StockCard
          stock={stock}
          onAddToWatchlist={
            handleAddToWatchlist
          }
          isAdding={isAdding}
          watchlistMessage={
            watchlistMessage
          }
        />
      )}
    </section>
  );
}