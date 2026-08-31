"use client";

import { useEffect, useState } from "react";

import MarketAnalysisPanel from "@/components/analysis/MarketAnalysisPanel";
import StockChart from "@/components/stocks/StockChart";
import {
  getStockQuote,
  getWatchlist,
  removeFromWatchlist,
  runMarketAnalysis,
} from "@/services/api";
import type { MarketAnalysisResult } from "@/types/analysis";
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

  const [expandedSymbol, setExpandedSymbol] = useState<
    string | null
  >(null);

  const [analysisBySymbol, setAnalysisBySymbol] = useState<
    Record<string, MarketAnalysisResult>
  >({});

  const [analyzingSymbol, setAnalyzingSymbol] = useState<
    string | null
  >(null);

  const [analysisErrors, setAnalysisErrors] = useState<
    Record<string, string>
  >({});

  useEffect(() => {
    let cancelled = false;

    async function loadInitialWatchlist() {
      try {
        const watchlistStocks =
          await fetchWatchlistStocks();

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

    const intervalId = window.setInterval(() => {
      void loadInitialWatchlist();
    }, 60000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  async function handleRefresh() {
    try {
      setIsLoading(true);
      setError("");

      const watchlistStocks =
        await fetchWatchlistStocks();

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

      if (expandedSymbol === symbol) {
        setExpandedSymbol(null);
      }

      setAnalysisBySymbol((current) => {
        const updated = { ...current };

        delete updated[symbol];

        return updated;
      });
    } catch {
      setError(
        `Could not remove ${symbol} from watchlist.`,
      );
    }
  }

  function handleToggle(symbol: string) {
    setExpandedSymbol((current) =>
      current === symbol ? null : symbol,
    );
  }

  async function handleRunAnalysis(
    symbol: string,
  ) {
    try {
      setAnalyzingSymbol(symbol);

      setAnalysisErrors((current) => ({
        ...current,
        [symbol]: "",
      }));

      const result = await runMarketAnalysis(symbol);

      setAnalysisBySymbol((current) => ({
        ...current,
        [symbol]: result,
      }));
    } catch (analysisError) {
      const message =
        analysisError instanceof Error
          ? analysisError.message
          : `Could not analyze ${symbol}.`;

      setAnalysisErrors((current) => ({
        ...current,
        [symbol]: message,
      }));
    } finally {
      setAnalyzingSymbol(null);
    }
  }

  return (
    <section className="mt-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold">
              Watchlist
            </h2>

            {!isLoading && (
              <span className="rounded-full border border-gray-700 bg-gray-900 px-2.5 py-1 text-xs text-gray-400">
                {stocks.length} saved
              </span>
            )}
          </div>

          <p className="mt-2 text-sm text-gray-500">
            Track saved stocks and expand one to view
            price history and MarketSignal analysis.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={isLoading}
          className="rounded-lg border border-gray-700 bg-gray-950 px-4 py-2 text-sm font-medium transition hover:border-gray-500 hover:bg-gray-900 disabled:opacity-50"
        >
          {isLoading
            ? "Refreshing..."
            : "Refresh Quotes"}
        </button>
      </div>

      {error && (
        <div className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {isLoading && stocks.length === 0 && (
        <div className="mt-5 rounded-xl border border-gray-800 bg-gray-950/40 p-6 text-sm text-gray-500">
          Loading watchlist...
        </div>
      )}

      {!isLoading
        && !error
        && stocks.length === 0 && (
          <div className="mt-5 rounded-xl border border-dashed border-gray-700 bg-gray-950/30 p-8 text-center">
            <p className="font-medium">
              Your watchlist is empty
            </p>

            <p className="mt-2 text-sm text-gray-500">
              Search for a stock below and add it to
              your watchlist.
            </p>
          </div>
        )}

      {stocks.length > 0 && (
        <div className="mt-5 space-y-4">
          {stocks.map(({ item, quote }) => {
            const symbol = item.symbol;

            const isExpanded =
              expandedSymbol === symbol;

            const analysis =
              analysisBySymbol[symbol];

            const analysisError =
              analysisErrors[symbol];

            const isAnalyzing =
              analyzingSymbol === symbol;

            const isPositive =
              quote !== null
                ? quote.change >= 0
                : false;

            return (
              <article
                key={item.id}
                className={`overflow-hidden rounded-2xl border bg-gray-950/30 transition ${
                  isExpanded
                    ? "border-gray-600"
                    : "border-gray-800 hover:border-gray-700"
                }`}
              >
                <div className="flex items-stretch">
                  <button
                    type="button"
                    onClick={() =>
                      handleToggle(symbol)
                    }
                    className="flex flex-1 items-center justify-between gap-5 p-5 text-left"
                  >
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-3">
                        <span className="text-sm font-medium text-gray-500">
                          {symbol}
                        </span>

                        {quote && (
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                              isPositive
                                ? "bg-green-500/10 text-green-400"
                                : "bg-red-500/10 text-red-400"
                            }`}
                          >
                            {quote.change_percent >= 0
                              ? "+"
                              : ""}
                            {quote.change_percent.toFixed(
                              2,
                            )}
                            %
                          </span>
                        )}
                      </div>

                      {quote ? (
                        <>
                          <h3 className="mt-1 text-lg font-semibold text-gray-100">
                            {quote.company_name}
                          </h3>

                          <p className="mt-2 text-2xl font-bold">
                            {quote.currency}{" "}
                            {quote.price.toFixed(2)}
                          </p>
                        </>
                      ) : (
                        <>
                          <h3 className="mt-1 text-lg font-semibold text-gray-100">
                            {symbol}
                          </h3>

                          <p className="mt-2 text-sm text-gray-500">
                            Market data unavailable
                          </p>
                        </>
                      )}
                    </div>

                    <div className="flex shrink-0 items-center gap-4">
                      <span className="hidden text-xs text-gray-500 sm:block">
                        {isExpanded
                          ? "Hide details"
                          : "View details"}
                      </span>

                      <svg
                        viewBox="0 0 20 20"
                        fill="none"
                        aria-hidden="true"
                        className={`h-5 w-5 text-gray-400 transition-transform ${
                          isExpanded
                            ? "rotate-180"
                            : ""
                        }`}
                      >
                        <path
                          d="M5 7.5L10 12.5L15 7.5"
                          stroke="currentColor"
                          strokeWidth="1.7"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </div>
                  </button>

                  <div className="flex items-center border-l border-gray-800 px-4">
                    <button
                      type="button"
                      onClick={() =>
                        handleRemove(symbol)
                      }
                      className="rounded-lg border border-red-500/30 px-3 py-2 text-sm text-red-400 transition hover:bg-red-500/10"
                    >
                      Remove
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="border-t border-gray-800 p-5 md:p-6">
                    {quote && (
                      <div>
                        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                          <div>
                            <h4 className="text-lg font-semibold">
                              Price History
                            </h4>

                            <p className="mt-1 text-sm text-gray-500">
                              Explore recent price movement
                              across multiple time periods.
                            </p>
                          </div>

                          <p className="text-sm text-gray-500">
                            Current:{" "}
                            <span className="font-medium text-gray-200">
                              {quote.currency}{" "}
                              {quote.price.toFixed(2)}
                            </span>
                          </p>
                        </div>

                        <StockChart symbol={symbol} />
                      </div>
                    )}

                    <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-gray-800 bg-black/20 p-4">
                      <div>
                        <p className="font-semibold">
                          MarketSignal Analysis
                        </p>

                        <p className="mt-1 text-sm text-gray-500">
                          {analysis
                            ? "The latest analysis run during this session is shown below."
                            : "Run the analysis to evaluate recent news and market events."}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          handleRunAnalysis(symbol)
                        }
                        disabled={isAnalyzing}
                        className="rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {isAnalyzing
                          ? "Analyzing..."
                          : analysis
                            ? "Run New Analysis"
                            : "Run Market Analysis"}
                      </button>
                    </div>

                    {isAnalyzing && (
                      <div className="mt-4 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                        <div className="flex items-center gap-3">
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-600 border-t-blue-400" />

                          <div>
                            <p className="text-sm font-medium">
                              Running MarketSignal analysis
                            </p>

                            <p className="mt-1 text-xs text-gray-500">
                              Collecting news, analyzing
                              sentiment, clustering events,
                              and building the outlook.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {analysisError && (
                      <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
                        {analysisError}
                      </div>
                    )}

                    {analysis && (
                      <MarketAnalysisPanel
                        analysis={analysis}
                      />
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}