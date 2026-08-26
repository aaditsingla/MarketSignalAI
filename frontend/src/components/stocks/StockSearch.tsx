"use client";

import { FormEvent, useState } from "react";

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
  const [stock, setStock] = useState<StockQuote | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [watchlistMessage, setWatchlistMessage] = useState("");

  

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
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

      const stockData = await getStockQuote(trimmedSymbol);

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

  async function handleAddToWatchlist(stockSymbol: string) {
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
    <section className="mt-10">
      <form onSubmit={handleSubmit} className="flex max-w-xl gap-3">
        <input
          type="text"
          value={symbol}
          onChange={(event) => setSymbol(event.target.value)}
          placeholder="Search ticker, e.g. NVDA"
          className="flex-1 rounded-lg border px-4 py-3 outline-none"
        />

        <button
          type="submit"
          disabled={isLoading}
          className="rounded-lg bg-white px-6 py-3 font-medium text-black disabled:opacity-50"
        >
          {isLoading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && (
        <p className="mt-4 text-red-500">
          {error}
        </p>
      )}

      {stock && (
        <StockCard
          stock={stock}
          onAddToWatchlist={handleAddToWatchlist}
          isAdding={isAdding}
          watchlistMessage={watchlistMessage}
        />
      )}
    </section>
  );
}