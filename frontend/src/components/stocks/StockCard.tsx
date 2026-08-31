"use client";

import { useState } from "react";

import MarketAnalysisPanel from "@/components/analysis/MarketAnalysisPanel";
import StockChart from "@/components/stocks/StockChart";
import { runMarketAnalysis } from "@/services/api";
import type { MarketAnalysisResult } from "@/types/analysis";
import type { StockQuote } from "@/types/stock";

interface StockCardProps {
  stock: StockQuote;
  onAddToWatchlist: (
    symbol: string,
  ) => Promise<void>;
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

  const [isAnalyzing, setIsAnalyzing] =
    useState(false);

  const [analysisError, setAnalysisError] =
    useState("");

  async function handleRunAnalysis() {
    try {
      setIsAnalyzing(true);
      setAnalysisError("");

      const result =
        await runMarketAnalysis(stock.symbol);

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
    <section className="mt-6 overflow-hidden rounded-2xl border border-gray-800 bg-gray-950/30">
      <div className="p-5 md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <span className="rounded-full border border-gray-700 bg-gray-900 px-2.5 py-1 text-xs font-medium text-gray-400">
                {stock.symbol}
              </span>

              <span
                className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                  isPositive
                    ? "bg-green-500/10 text-green-400"
                    : "bg-red-500/10 text-red-400"
                }`}
              >
                {stock.change_percent >= 0
                  ? "+"
                  : ""}
                {stock.change_percent.toFixed(2)}%
              </span>
            </div>

            <h2 className="mt-3 text-2xl font-bold">
              {stock.company_name}
            </h2>

            <div className="mt-3 flex flex-wrap items-end gap-3">
              <p className="text-4xl font-bold">
                {stock.currency}{" "}
                {stock.price.toFixed(2)}
              </p>

              <p
                className={`pb-1 text-sm font-medium ${
                  isPositive
                    ? "text-green-400"
                    : "text-red-400"
                }`}
              >
                {stock.change >= 0 ? "+" : ""}
                {stock.change.toFixed(2)}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleRunAnalysis}
              disabled={isAnalyzing}
              className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isAnalyzing
                ? "Analyzing..."
                : marketAnalysis
                  ? "Run New Analysis"
                  : "Run Market Analysis"}
            </button>

            <button
              type="button"
              onClick={() =>
                onAddToWatchlist(
                  stock.symbol,
                )
              }
              disabled={isAdding}
              className="rounded-lg border border-gray-700 px-4 py-2.5 text-sm font-medium transition hover:border-gray-500 hover:bg-gray-900 disabled:opacity-50"
            >
              {isAdding
                ? "Adding..."
                : "Add to Watchlist"}
            </button>
          </div>
        </div>

        {watchlistMessage && (
          <p className="mt-4 text-sm text-gray-400">
            {watchlistMessage}
          </p>
        )}

        {analysisError && (
          <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
            {analysisError}
          </div>
        )}

        {isAnalyzing && (
          <div className="mt-5 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
            <div className="flex items-center gap-3">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-600 border-t-blue-400" />

              <div>
                <p className="text-sm font-medium">
                  Building MarketSignal outlook
                </p>

                <p className="mt-1 text-xs text-gray-500">
                  Collecting news, processing
                  sentiment, and analyzing events.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid border-y border-gray-800 sm:grid-cols-2 lg:grid-cols-4">
        <div className="border-b border-gray-800 p-4 sm:border-r lg:border-b-0">
          <p className="text-xs uppercase tracking-wide text-gray-500">
            Previous Close
          </p>

          <p className="mt-2 font-semibold">
            {stock.currency}{" "}
            {stock.previous_close.toFixed(2)}
          </p>
        </div>

        <div className="border-b border-gray-800 p-4 lg:border-b-0 lg:border-r">
          <p className="text-xs uppercase tracking-wide text-gray-500">
            Market Cap
          </p>

          <p className="mt-2 font-semibold">
            {stock.market_cap !== null
              ? stock.market_cap.toLocaleString()
              : "N/A"}
          </p>
        </div>

        <div className="border-b border-gray-800 p-4 sm:border-r sm:border-b-0">
          <p className="text-xs uppercase tracking-wide text-gray-500">
            52 Week High
          </p>

          <p className="mt-2 font-semibold">
            {stock.fifty_two_week_high !==
            null
              ? stock.fifty_two_week_high.toFixed(
                  2,
                )
              : "N/A"}
          </p>
        </div>

        <div className="p-4">
          <p className="text-xs uppercase tracking-wide text-gray-500">
            52 Week Low
          </p>

          <p className="mt-2 font-semibold">
            {stock.fifty_two_week_low !==
            null
              ? stock.fifty_two_week_low.toFixed(
                  2,
                )
              : "N/A"}
          </p>
        </div>
      </div>

      <div className="p-5 md:p-6">
        <StockChart symbol={stock.symbol} />

        {marketAnalysis && (
          <MarketAnalysisPanel
            analysis={marketAnalysis}
          />
        )}
      </div>
    </section>
  );
}