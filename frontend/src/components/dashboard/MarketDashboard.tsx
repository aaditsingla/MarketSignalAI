"use client";

import { useState } from "react";

import StockSearch from "@/components/stocks/StockSearch";
import Watchlist from "@/components/watchlist/Watchlist";

export default function MarketDashboard() {
  const [watchlistVersion, setWatchlistVersion] = useState(0);

  function handleWatchlistChanged() {
    setWatchlistVersion((currentVersion) => currentVersion + 1);
  }

  return (
    <>
      <Watchlist key={watchlistVersion} />

      <StockSearch onWatchlistChanged={handleWatchlistChanged} />
    </>
  );
}