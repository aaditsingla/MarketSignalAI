export async function getApiHealth() {
  const response = await fetch("http://127.0.0.1:8000/health", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to connect to MarketSignal API");
  }

  return response.json();
}