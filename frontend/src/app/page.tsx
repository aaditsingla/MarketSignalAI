import { getApiHealth } from "@/services/api";

export default async function Home() {
  const health = await getApiHealth();

  return (
    <main className="min-h-screen p-10">
      <h1 className="text-4xl font-bold">MarketSignal AI</h1>

      <p className="mt-2 text-gray-500">
        AI-powered market intelligence and trading education.
      </p>

      <div className="mt-8 rounded-lg border p-4">
        <h2 className="text-xl font-semibold">Backend Status</h2>

        <p className="mt-2">
          {health.service}: {health.status}
        </p>
      </div>
    </main>
  );
}