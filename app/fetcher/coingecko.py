import httpx
from typing import Dict, Any, List

# Base URL of the CoinGecko REST API
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

async def fetch_prices_from_coingecko(coin_ids: List[str]) -> Dict[str, Any]:
    """
    Fetches current prices for the given coin identifiers (e.g. ['bitcoin', 'ethereum', 'solana']).
    Returns a JSON dictionary with USD prices, 24h change, market cap and volume.
    """
    ids_param = ",".join(coin_ids)
    params = {
        "ids": ids_param,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }

    headers = {
        "User-Agent": "CryptoAlertBot/1.0"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(COINGECKO_API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
