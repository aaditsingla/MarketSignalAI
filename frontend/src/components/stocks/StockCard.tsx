"use client";

import { useState } from "react";

import MarketAnalysisPanel from "@/components/analysis/MarketAnalysisPanel";
import StockChart from "@/components/stocks/StockChart";
import { runMarketAnalysis } from "@/services/api";
import type { MarketAnalysisResult } from "@/types/analysis";
import type { StockQuote } from "@/types/stock";

interface StockCardProps {
  stock: StockQuote;
  onAddToWatchlist: (symbol: string) => Promise<void>;
  isAdding: boolean;
  watchlistMessage: string;
}

export default function StockCard({
  stock,
  onAddToWatchlist,
  isAdding,
  watchlistMessage,
}: StockCardProps) {
  const isPositive = stock.change >= 0;

  const [
    marketAnalysis,
    setMarketAnalysis,
  ] = useState<MarketAnalysisResult | null>(
    null,
  );

  const [
    isAnalyzing,
    setIsAnalyzing,
  ] = useState(false);

  const [
    analysisError,
    setAnalysisError,
  ] = useState("");

  async function handleRunAnalysis() {
    try {
      setIsAnalyzing(true);
      setAnalysisError("");

      const result = await runMarketAnalysis(
        stock.symbol,
      );

      setMarketAnalysis(result);
    } catch (error) {
      if (error instanceof Error) {
        setAnalysisError(error.message);
      } else {
        setAnalysisError(
          "Could not run market analysis.",
        );
      }
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <section className="mt-6 rounded-xl border p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-gray-500">
            {stock.symbol}
          </p>

          <h2 className="text-2xl font-semibold">
            {stock.company_name}
          </h2>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleRunAnalysis}
            disabled={isAnalyzing}
            className="rounded-lg border px-4 py-2 text-sm disabled:opacity-50"
          >
            {isAnalyzing
              ? "Analyzing..."
              : "Run Market Analysis"}
          </button>

          <button
            onClick={() =>
              onAddToWatchlist(stock.symbol)
            }
            disabled={isAdding}
            className="rounded-lg border px-4 py-2 text-sm disabled:opacity-50"
          >
            {isAdding
              ? "Adding..."
              : "Add to Watchlist"}
          </button>
        </div>
      </div>

      {watchlistMessage && (
        <p className="mt-3 text-sm text-gray-400">
          {watchlistMessage}
        </p>
      )}

      {analysisError && (
        <p className="mt-3 text-sm text-red-500">
          {analysisError}
        </p>
      )}

      <div className="mt-6">
        <p className="text-4xl font-bold">
          {stock.currency}{" "}
          {stock.price.toFixed(2)}
        </p>

        <p
          className={`mt-2 ${
            isPositive
              ? "text-green-500"
              : "text-red-500"
          }`}
        >
          {stock.change >= 0 ? "+" : ""}
          {stock.change.toFixed(2)}{" "}
          (
          {stock.change_percent >= 0
            ? "+"
            : ""}
          {stock.change_percent.toFixed(2)}%)
        </p>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <div>
          <p className="text-sm text-gray-500">
            Previous Close
          </p>

          <p className="font-medium">
            {stock.previous_close.toFixed(2)}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">
            Market Cap
          </p>

          <p className="font-medium">
            {stock.market_cap !== null
              ? stock.market_cap.toLocaleString()
              : "N/A"}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">
            52 Week High
          </p>

          <p className="font-medium">
            {stock.fifty_two_week_high !== null
              ? stock.fifty_two_week_high.toFixed(2)
              : "N/A"}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">
            52 Week Low
          </p>

          <p className="font-medium">
            {stock.fifty_two_week_low !== null
              ? stock.fifty_two_week_low.toFixed(2)
              : "N/A"}
          </p>
        </div>
      </div>

      <StockChart symbol={stock.symbol} />

      {marketAnalysis && (
        <MarketAnalysisPanel
          analysis={marketAnalysis}
        />
      )}
    </section>
  );
}