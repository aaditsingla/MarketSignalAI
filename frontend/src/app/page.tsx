import MarketDashboard from "@/components/dashboard/MarketDashboard";

export default function Home() {
  return (
    <main className="min-h-screen">
      <div className="mx-auto w-full max-w-[1800px] px-5 py-8 sm:px-8 md:py-10 lg:px-10">
        <header className="border-b border-gray-800 pb-8">
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-blue-500/30 bg-blue-500/10 font-bold text-blue-400">
                  M
                </div>

                <div>
                  <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                    MarketSignal AI
                  </h1>

                  <p className="mt-1 text-sm text-gray-500">
                    AI powered market intelligence
                    and trading research.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-full border border-gray-800 bg-gray-950/60 px-3 py-1.5 text-xs text-gray-500">
              News intelligence dashboard
            </div>
          </div>
        </header>

        <MarketDashboard />

        <footer className="mt-16 border-t border-gray-800 py-8 text-xs text-gray-600">
          MarketSignal AI is an educational
          research project. Market outlooks are
          not investment advice.
        </footer>
      </div>
    </main>
  );
}