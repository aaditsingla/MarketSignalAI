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
        word.charAt(0).toUpperCase()
        + word.slice(1),
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

function EventList({
  events,
  emptyMessage,
}: {
  events: OutlookEvent[];
  emptyMessage: string;
}) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        {emptyMessage}
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <div
          key={`${event.category}-${event.article_ids.join("-")}`}
          className="rounded-lg border p-3"
        >
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium uppercase text-gray-500">
              {formatLabel(event.category)}
            </span>

            {event.unique_sources > 1 && (
              <span className="text-xs text-gray-500">
                {event.unique_sources} sources
              </span>
            )}
          </div>

          <p className="mt-1 text-sm font-medium">
            {event.title}
          </p>

          <p className="mt-1 text-xs text-gray-500">
            Directional score:{" "}
            {formatScore(event.directional_score)}
          </p>
        </div>
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

  return (
    <section className="mt-8 rounded-xl border p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-gray-500">
            MarketSignal News Outlook
          </p>

          <h3 className="mt-1 text-2xl font-semibold">
            {formatLabel(summary.direction)}
          </h3>

          <p className="mt-2 text-sm text-gray-400">
            Based on recent company news and market events.
          </p>
        </div>

        <div className="text-right">
          <p className="text-sm text-gray-500">
            Directional Score
          </p>

          <p className="text-xl font-semibold">
            {formatScore(summary.directional_score)}
          </p>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <div>
          <p className="text-sm text-gray-500">
            Conviction
          </p>

          <p className="font-medium">
            {formatLabel(summary.conviction)}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">
            News Agreement
          </p>

          <p className="font-medium">
            {formatLabel(summary.news_agreement)}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">
            Events Analyzed
          </p>

          <p className="font-medium">
            {summary.events_analyzed}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">
            Analysis Price
          </p>

          <p className="font-medium">
            USD {analysis.analysis.stock_price.toFixed(2)}
          </p>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3">
          <p className="text-xs text-gray-500">
            Positive
          </p>

          <p className="mt-1 font-semibold">
            {formatPercent(summary.positive_score)}
          </p>
        </div>

        <div className="rounded-lg border p-3">
          <p className="text-xs text-gray-500">
            Neutral
          </p>

          <p className="mt-1 font-semibold">
            {formatPercent(summary.neutral_score)}
          </p>
        </div>

        <div className="rounded-lg border p-3">
          <p className="text-xs text-gray-500">
            Negative
          </p>

          <p className="mt-1 font-semibold">
            {formatPercent(summary.negative_score)}
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div>
          <h4 className="mb-3 text-lg font-semibold">
            Positive Catalysts
          </h4>

          <EventList
            events={outlook.positive_catalysts}
            emptyMessage="No strong positive catalysts identified."
          />
        </div>

        <div>
          <h4 className="mb-3 text-lg font-semibold">
            Negative Risks
          </h4>

          <EventList
            events={outlook.negative_risks}
            emptyMessage="No strong negative risks identified."
          />
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div>
          <h4 className="mb-3 text-lg font-semibold">
            Supporting Positive Signals
          </h4>

          <EventList
            events={outlook.positive_signals}
            emptyMessage="No additional positive market signals."
          />
        </div>

        <div>
          <h4 className="mb-3 text-lg font-semibold">
            Supporting Negative Signals
          </h4>

          <EventList
            events={outlook.negative_signals}
            emptyMessage="No additional negative market signals."
          />
        </div>
      </div>

      <div className="mt-8 rounded-lg border p-4">
        <h4 className="font-semibold">
          Analysis Trend
        </h4>

        {comparison.previous ? (
          <div className="mt-3 grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm text-gray-500">
                Trend
              </p>

              <p className="font-medium">
                {formatLabel(comparison.trend)}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-500">
                Previous Direction
              </p>

              <p className="font-medium">
                {formatLabel(
                  comparison.previous.direction,
                )}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-500">
                Score Change
              </p>

              <p className="font-medium">
                {comparison.score_change !== null
                  ? formatScore(
                      comparison.score_change,
                    )
                  : "N/A"}
              </p>
            </div>
          </div>
        ) : (
          <p className="mt-2 text-sm text-gray-500">
            No previous analysis is available yet.
          </p>
        )}
      </div>

      <p className="mt-6 text-xs text-gray-500">
        This outlook summarizes recent news evidence and is
        not investment advice.
      </p>
    </section>
  );
}