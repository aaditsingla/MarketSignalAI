export interface OutlookEvent {
  title: string;
  category: string;
  directional_score: number;
  unique_sources: number;
  article_ids: number[];
}

export interface MarketOutlook {
  symbol: string;
  positive_catalysts: OutlookEvent[];
  negative_risks: OutlookEvent[];
  positive_signals: OutlookEvent[];
  negative_signals: OutlookEvent[];
  events_analyzed: number;
}

export interface SignalSummary {
  symbol: string;
  direction:
    | "bullish"
    | "slightly_bullish"
    | "neutral"
    | "slightly_bearish"
    | "bearish";

  conviction: "low" | "moderate" | "high";

  news_agreement:
    | "consistent"
    | "mixed"
    | "conflicting";

  directional_score: number;
  agreement_score: number;

  positive_score: number;
  neutral_score: number;
  negative_score: number;

  events_analyzed: number;
}

export interface AnalysisSnapshotSummary {
  analysis_id: number;
  analyzed_at: string;
  stock_price: number;
  direction: string;
  directional_score: number;
}

export interface AnalysisComparison {
  symbol: string;

  current: AnalysisSnapshotSummary;

  previous: AnalysisSnapshotSummary | null;

  score_change: number | null;
  price_change_percent: number | null;

  trend:
    | "improving"
    | "weakening"
    | "stable"
    | "no_previous_analysis";
}

export interface StoredAnalysis {
  id: number;
  symbol: string;
  stock_price: number;

  signal: string;
  confidence: number;

  sentiment_score: number;

  positive_score: number;
  neutral_score: number;
  negative_score: number;

  articles_analyzed: number;

  analyzed_at: string;
}

export interface SentimentProcessing {
  articles_with_content: number;
  newly_analyzed: number;
  reused_existing: number;
  failed: number;
}

export interface NewsProcessing {
  discovered: number;
  relevant: number;
  stored_or_linked: number;
  content_scraped: number;
}

export interface MarketAnalysisResult {
  symbol: string;

  news: NewsProcessing;

  sentiment_processing: SentimentProcessing;

  events_analyzed: number;

  signal_summary: SignalSummary;

  outlook: MarketOutlook;

  analysis: StoredAnalysis;

  comparison: AnalysisComparison;
}