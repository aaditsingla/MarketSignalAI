import yfinance as yf

from app.models.stock import StockQuote
from app.models.stock_history import HistoricalPricePoint, StockHistory


class MarketService:
    def get_stock_quote(self, symbol: str) -> StockQuote:
        ticker_symbol = symbol.upper().strip()
        ticker = yf.Ticker(ticker_symbol)

        info = ticker.info

        price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")

        if price is None or previous_close is None:
            raise ValueError(f"Could not retrieve market data for {ticker_symbol}")

        change = price - previous_close
        change_percent = (change / previous_close) * 100

        return StockQuote(
            symbol=ticker_symbol,
            company_name=info.get("longName") or info.get("shortName") or ticker_symbol,
            price=price,
            previous_close=previous_close,
            change=change,
            change_percent=change_percent,
            market_cap=info.get("marketCap"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            currency=info.get("currency", "USD"),
        )

    def get_stock_history(self, symbol: str, period: str) -> StockHistory:
        ticker_symbol = symbol.upper().strip()

        allowed_periods = {
            "1d": "1d",
            "1mo": "1mo",
            "6mo": "6mo",
            "1y": "1y",
        }

        if period not in allowed_periods:
            raise ValueError(f"Unsupported period: {period}")

        ticker = yf.Ticker(ticker_symbol)

        interval = "5m" if period == "1d" else "1d"

        history = ticker.history(
            period=allowed_periods[period],
            interval=interval,
        )

        if history.empty:
            raise ValueError(
                f"Could not retrieve historical data for {ticker_symbol}"
            )

        prices = [
            HistoricalPricePoint(
                timestamp=index.to_pydatetime(),
                close=float(row["Close"]),
            )
            for index, row in history.iterrows()
        ]

        return StockHistory(
            symbol=ticker_symbol,
            period=period,
            prices=prices,
        )