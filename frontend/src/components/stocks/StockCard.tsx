import type { StockQuote } from "@/types/stock";
import StockChart from "@/components/stocks/StockChart";

interface StockCardProps {
  stock: StockQuote;
}

export default function StockCard({ stock }: StockCardProps) {
  const isPositive = stock.change >= 0;

  return (
    <section className="mt-6 rounded-xl border p-6">
      <div>
        <p className="text-sm text-gray-500">{stock.symbol}</p>

        <h2 className="text-2xl font-semibold">
          {stock.company_name}
        </h2>
      </div>

      <div className="mt-6">
        <p className="text-4xl font-bold">
          {stock.currency} {stock.price.toFixed(2)}
        </p>

        <p className={`mt-2 ${isPositive ? "text-green-500" : "text-red-500"}`}>
          {stock.change >= 0 ? "+" : ""}
          {stock.change.toFixed(2)}{" "}
          ({stock.change_percent >= 0 ? "+" : ""}
          {stock.change_percent.toFixed(2)}%)
        </p>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <div>
          <p className="text-sm text-gray-500">Previous Close</p>
          <p className="font-medium">
            {stock.previous_close.toFixed(2)}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">Market Cap</p>
          <p className="font-medium">
            {stock.market_cap !== null
              ? stock.market_cap.toLocaleString()
              : "N/A"}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">52 Week High</p>
          <p className="font-medium">
            {stock.fifty_two_week_high !== null
              ? stock.fifty_two_week_high.toFixed(2)
              : "N/A"}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-500">52 Week Low</p>
          <p className="font-medium">
            {stock.fifty_two_week_low !== null
              ? stock.fifty_two_week_low.toFixed(2)
              : "N/A"}
          </p>
        </div>
      </div>
      <StockChart symbol={stock.symbol} />
    </section>
  );
}