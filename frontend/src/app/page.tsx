import StockSearch from "@/components/stocks/StockSearch";

export default function Home() {
  return (
    <main className="min-h-screen p-10">
      <h1 className="text-4xl font-bold">MarketSignal AI</h1>

      <p className="mt-2 text-gray-500">
        AI-powered market intelligence and trading education.
      </p>

      <StockSearch />
    </main>
  );
}