import type {
  MarketAnalysisResult,
  OutlookEvent,
} from "@/types/analysis";

interface MarketAnalysisPanelProps {
  analysis: MarketAnalysisResult;
}

function formatLabel(value: string): string {
  return value
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatScore(value: number): string {
  const prefix = value > 0 ? "+" : "";

  return `${prefix}${value.toFixed(3)}`;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function getDirectionClasses(direction: string): string {
  if (
    direction === "bullish"
    || direction === "slightly_bullish"
  ) {
    return "border-green-500/40 bg-green-500/10 text-green-400";
  }

  if (
    direction === "bearish"
    || direction === "slightly_bearish"
  ) {
    return "border-red-500/40 bg-red-500/10 text-red-400";
  }

  return "border-gray-600 bg-gray-800/40 text-gray-300";
}

function getTrendClasses(trend: string): string {
  if (trend === "improving") {
    return "text-green-400";
  }

  if (trend === "weakening") {
    return "text-red-400";
  }

  return "text-gray-300";
}

function getEventTone(
  score: number,
): string {
  if (score > 0) {
    return "border-green-500/20";
  }

  if (score < 0) {
    return "border-red-500/20";
  }

  return "border-gray-700";
}

function EventList({
  events,
  emptyMessage,
}: {
  events: OutlookEvent[];
  emptyMessage: string;
}) {
  if (events.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-700 p-4">
        <p className="text-sm text-gray-500">
          {emptyMessage}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <article
          key={`${event.category}-${event.article_ids.join("-")}`}
          className={`rounded-lg border bg-black/20 p-4 ${getEventTone(
            event.directional_score,
          )}`}
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="rounded-full bg-gray-800 px-2.5 py-1 text-xs font-medium text-gray-300">
              {formatLabel(event.category)}
            </span>

            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span>
                Score {formatScore(event.directional_score)}
              </span>

              <span>
                {event.unique_sources}{" "}
                {event.unique_sources === 1
                  ? "source"
                  : "sources"}
              </span>
            </div>
          </div>

          <p className="mt-3 text-sm font-medium leading-6 text-gray-100">
            {event.title}
          </p>
        </article>
      ))}
    </div>
  );
}

export default function MarketAnalysisPanel({
  analysis,
}: MarketAnalysisPanelProps) {
  const summary = analysis.signal_summary;
  const outlook = analysis.outlook;
  const comparison = analysis.comparison;

  const positivePercent =
    summary.positive_score * 100;

  const neutralPercent =
    summary.neutral_score * 100;

  const negativePercent =
    summary.negative_score * 100;

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-gray-700 bg-gray-950/40">
      <div className="border-b border-gray-800 p-6">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
              MarketSignal News Outlook
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-3">
              <h3 className="text-3xl font-bold">
                {formatLabel(summary.direction)}
              </h3>

              <span
                className={`rounded-full border px-3 py-1 text-sm font-medium ${getDirectionClasses(
                  summary.direction,
                )}`}
              >
                {formatLabel(summary.conviction)} Conviction
              </span>
            </div>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-gray-400">
              Analysis of recent company news, market events,
              financial sentiment, and supporting signals.
            </p>
          </div>

          <div className="rounded-xl border border-gray-700 bg-black/30 px-5 py-4 text-right">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Directional Score
            </p>

            <p className="mt-1 text-2xl font-bold">
              {formatScore(summary.directional_score)}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              {formatDate(analysis.analysis.analyzed_at)}
            </p>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Conviction
            </p>

            <p className="mt-2 text-lg font-semibold">
              {formatLabel(summary.conviction)}
            </p>
          </div>

          <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              News Agreement
            </p>

            <p className="mt-2 text-lg font-semibold">
              {formatLabel(summary.news_agreement)}
            </p>
          </div>

          <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Events Analyzed
            </p>

            <p className="mt-2 text-lg font-semibold">
              {summary.events_analyzed}
            </p>
          </div>

          <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Analysis Price
            </p>

            <p className="mt-2 text-lg font-semibold">
              USD {analysis.analysis.stock_price.toFixed(2)}
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-xl border border-gray-800 bg-black/20 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h4 className="font-semibold">
              News Sentiment Distribution
            </h4>

            <p className="text-xs text-gray-500">
              FinBERT aggregated across unique events
            </p>
          </div>

          <div className="mt-5 space-y-4">
            <div>
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-green-400">
                  Positive
                </span>

                <span>
                  {formatPercent(summary.positive_score)}
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-gray-800">
                <div
                  className="h-full rounded-full bg-green-500"
                  style={{
                    width: `${positivePercent}%`,
                  }}
                />
              </div>
            </div>

            <div>
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-gray-300">
                  Neutral
                </span>

                <span>
                  {formatPercent(summary.neutral_score)}
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-gray-800">
                <div
                  className="h-full rounded-full bg-gray-400"
                  style={{
                    width: `${neutralPercent}%`,
                  }}
                />
              </div>
            </div>

            <div>
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-red-400">
                  Negative
                </span>

                <span>
                  {formatPercent(summary.negative_score)}
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-gray-800">
                <div
                  className="h-full rounded-full bg-red-500"
                  style={{
                    width: `${negativePercent}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-8 xl:grid-cols-2">
          <div>
            <div className="mb-4">
              <h4 className="text-lg font-semibold">
                Positive Catalysts
              </h4>

              <p className="mt-1 text-sm text-gray-500">
                Recent fundamental developments with positive
                directional sentiment.
              </p>
            </div>

            <EventList
              events={outlook.positive_catalysts}
              emptyMessage="No strong positive catalysts identified."
            />
          </div>

          <div>
            <div className="mb-4">
              <h4 className="text-lg font-semibold">
                Negative Risks
              </h4>

              <p className="mt-1 text-sm text-gray-500">
                Recent fundamental developments with negative
                directional sentiment.
              </p>
            </div>

            <EventList
              events={outlook.negative_risks}
              emptyMessage="No strong negative risks identified."
            />
          </div>
        </div>

        <div className="mt-10 border-t border-gray-800 pt-8">
          <h4 className="text-lg font-semibold">
            Supporting Market Signals
          </h4>

          <p className="mt-1 text-sm text-gray-500">
            Analyst, insider, and market activity shown separately
            from fundamental catalysts.
          </p>

          <div className="mt-5 grid gap-8 xl:grid-cols-2">
            <div>
              <h5 className="mb-3 font-medium text-green-400">
                Positive Signals
              </h5>

              <EventList
                events={outlook.positive_signals}
                emptyMessage="No additional positive market signals."
              />
            </div>

            <div>
              <h5 className="mb-3 font-medium text-red-400">
                Negative Signals
              </h5>

              <EventList
                events={outlook.negative_signals}
                emptyMessage="No additional negative market signals."
              />
            </div>
          </div>
        </div>

        <div className="mt-10 border-t border-gray-800 pt-8">
          <h4 className="text-lg font-semibold">
            Analysis Trend
          </h4>

          {comparison.previous ? (
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Trend
                </p>

                <p
                  className={`mt-2 font-semibold ${getTrendClasses(
                    comparison.trend,
                  )}`}
                >
                  {formatLabel(comparison.trend)}
                </p>
              </div>

              <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Previous Direction
                </p>

                <p className="mt-2 font-semibold">
                  {formatLabel(
                    comparison.previous.direction,
                  )}
                </p>
              </div>

              <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Score Change
                </p>

                <p className="mt-2 font-semibold">
                  {comparison.score_change !== null
                    ? formatScore(
                        comparison.score_change,
                      )
                    : "N/A"}
                </p>
              </div>

              <div className="rounded-xl border border-gray-800 bg-black/20 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Price Change
                </p>

                <p className="mt-2 font-semibold">
                  {comparison.price_change_percent !== null
                    ? `${comparison.price_change_percent >= 0 ? "+" : ""}${comparison.price_change_percent.toFixed(2)}%`
                    : "N/A"}
                </p>
              </div>
            </div>
          ) : (
            <div className="mt-4 rounded-xl border border-dashed border-gray-700 p-5">
              <p className="text-sm text-gray-500">
                No previous analysis is available yet. Future
                analyses will be compared against this snapshot.
              </p>
            </div>
          )}
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-gray-800 pt-5 text-xs text-gray-500">
          <p>
            This outlook summarizes recent news evidence and is
            not investment advice.
          </p>

          <p>
            Analysis #{analysis.analysis.id}
          </p>
        </div>
      </div>
    </section>
  );
}