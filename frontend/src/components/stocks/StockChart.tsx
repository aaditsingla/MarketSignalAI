"use client";

import { useEffect, useState } from "react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getStockHistory } from "@/services/api";
import type {
  StockHistory,
  StockHistoryPeriod,
} from "@/types/stockHistory";

interface StockChartProps {
  symbol: string;
}

const periods: { label: string; value: StockHistoryPeriod }[] = [
  { label: "1D", value: "1d" },
  { label: "1M", value: "1mo" },
  { label: "6M", value: "6mo" },
  { label: "1Y", value: "1y" },
];

export default function StockChart({ symbol }: StockChartProps) {
  const [period, setPeriod] = useState<StockHistoryPeriod>("1mo");
  const [history, setHistory] = useState<StockHistory | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        setIsLoading(true);
        setError("");

        const historyData = await getStockHistory(symbol, period);

        setHistory(historyData);
      } catch {
        setHistory(null);
        setError("Could not load historical price data.");
      } finally {
        setIsLoading(false);
      }
    }

    loadHistory();
  }, [symbol, period]);

  const chartData =
    history?.prices.map((point) => ({
      timestamp: new Date(point.timestamp).toLocaleDateString(),
      close: point.close,
    })) ?? [];

  return (
    <section className="mt-6 rounded-xl border p-6">
      <div className="flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Price History</h3>

        <div className="flex gap-2">
          {periods.map((option) => (
            <button
              key={option.value}
              onClick={() => setPeriod(option.value)}
              className={`rounded-md px-3 py-1 text-sm ${
                period === option.value
                  ? "bg-white text-black"
                  : "border text-gray-400"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 h-80">
        {isLoading && (
          <p className="text-gray-500">Loading chart...</p>
        )}

        {error && (
          <p className="text-red-500">{error}</p>
        )}

        {!isLoading && !error && chartData.length > 0 && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis
                dataKey="timestamp"
                tick={{ fontSize: 12 }}
                minTickGap={30}
              />

              <YAxis
                domain={["auto", "auto"]}
                tick={{ fontSize: 12 }}
              />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="close"
                stroke="currentColor"
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}