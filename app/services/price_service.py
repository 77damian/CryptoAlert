from sqlalchemy.orm import Session
from app.models.models import Coin, Price
from app.fetcher.coingecko import fetch_prices_from_coingecko

# Domyślna lista monet, które inicjalizujemy w systemie
INITIAL_COINS = [
    {"symbol": "BTC", "name": "Bitcoin", "coingecko_id": "bitcoin"},
    {"symbol": "ETH", "name": "Ethereum", "coingecko_id": "ethereum"},
    {"symbol": "SOL", "name": "Solana", "coingecko_id": "solana"}
]

def init_default_coins(db: Session):
    """Dodaje domyślne monety do bazy danych, jeśli jeszcze ich nie ma"""
    for coin_data in INITIAL_COINS:
        existing = db.query(Coin).filter(Coin.symbol == coin_data["symbol"]).first()
        if not existing:
            new_coin = Coin(
                symbol=coin_data["symbol"],
                name=coin_data["name"],
                coingecko_id=coin_data["coingecko_id"],
                is_active=True
            )
            db.add(new_coin)
    db.commit()


async def fetch_and_save_prices(db: Session):
    """
    1. Upewnia się, że monety są w bazie.
    2. Pobiera ceny z API.
    3. Zapisuje nowe rekordy w tabeli 'prices'.
    """
    init_default_coins(db)

    # Pobieramy aktywne monety z bazy
    active_coins = db.query(Coin).filter(Coin.is_active == True).all()
    if not active_coins:
        return []

    # Wyciągamy identyfikatory CoinGecko (np. ['bitcoin', 'ethereum', 'solana'])
    coingecko_ids = [coin.coingecko_id for coin in active_coins]
    
    # Pobieramy dane z zewnętrznego API
    api_data = await fetch_prices_from_coingecko(coingecko_ids)

    saved_prices = []
    for coin in active_coins:
        coin_info = api_data.get(coin.coingecko_id)
        if coin_info:
            new_price = Price(
                coin_id=coin.id,
                price_usd=coin_info.get("usd"),
                change_24h=coin_info.get("usd_24h_change"),
                market_cap=coin_info.get("usd_market_cap"),
                volume_24h=coin_info.get("usd_24h_vol")
            )
            db.add(new_price)
            saved_prices.append(new_price)

    db.commit()
    return saved_prices
