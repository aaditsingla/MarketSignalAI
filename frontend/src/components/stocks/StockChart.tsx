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

const periods: {
  label: string;
  value: StockHistoryPeriod;
}[] = [
  { label: "1D", value: "1d" },
  { label: "1M", value: "1mo" },
  { label: "6M", value: "6mo" },
  { label: "1Y", value: "1y" },
];

export default function StockChart({
  symbol,
}: StockChartProps) {
  const [period, setPeriod] =
    useState<StockHistoryPeriod>("1mo");

  const [history, setHistory] =
    useState<StockHistory | null>(null);

  const [isLoading, setIsLoading] =
    useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        setIsLoading(true);
        setError("");

        const historyData =
          await getStockHistory(
            symbol,
            period,
          );

        setHistory(historyData);
      } catch {
        setHistory(null);

        setError(
          "Could not load historical price data.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadHistory();
  }, [symbol, period]);

  const chartData =
    history?.prices.map((point) => ({
      timestamp: new Date(
        point.timestamp,
      ).toLocaleDateString(),
      close: point.close,
    })) ?? [];

  return (
    <section className="mt-6 rounded-xl border border-gray-700 bg-black/20 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">
          Price History
        </h3>

        <div className="flex gap-2">
          {periods.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() =>
                setPeriod(option.value)
              }
              className={`rounded-md px-3 py-1.5 text-sm transition ${
                period === option.value
                  ? "bg-white text-black"
                  : "border border-gray-600 text-gray-400 hover:border-gray-400 hover:text-gray-200"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 h-80">
        {isLoading && (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-gray-500">
              Loading chart...
            </p>
          </div>
        )}

        {error && (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-red-400">
              {error}
            </p>
          </div>
        )}

        {!isLoading
          && !error
          && chartData.length > 0 && (
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <LineChart
                data={chartData}
              >
                <XAxis
                  dataKey="timestamp"
                  tick={{
                    fontSize: 12,
                    fill: "#6b7280",
                  }}
                  axisLine={{
                    stroke: "#374151",
                  }}
                  tickLine={{
                    stroke: "#374151",
                  }}
                  minTickGap={30}
                />

                <YAxis
                  domain={[
                    "auto",
                    "auto",
                  ]}
                  tick={{
                    fontSize: 12,
                    fill: "#6b7280",
                  }}
                  axisLine={{
                    stroke: "#374151",
                  }}
                  tickLine={{
                    stroke: "#374151",
                  }}
                />

                <Tooltip
                  contentStyle={{
                    backgroundColor:
                      "#0b0f14",
                    border:
                      "1px solid #374151",
                    borderRadius:
                      "10px",
                    color: "#f3f4f6",
                    boxShadow:
                      "0 10px 30px rgba(0, 0, 0, 0.35)",
                  }}
                  labelStyle={{
                    color: "#9ca3af",
                    marginBottom: "6px",
                  }}
                  itemStyle={{
                    color: "#f3f4f6",
                  }}
                  cursor={{
                    stroke: "#6b7280",
                    strokeWidth: 1,
                  }}
                  formatter={(
                    value,
                  ) => [
                    `USD ${Number(
                      value,
                    ).toFixed(2)}`,
                    "Close",
                  ]}
                />

                <Line
                  type="monotone"
                  dataKey="close"
                  stroke="#f3f4f6"
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