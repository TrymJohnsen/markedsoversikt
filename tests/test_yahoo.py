from src.providers.yahoo import get_snapshot, get_price_history

ticker = "LYTIX.OL"  # Oslo Børs tickere bruker ofte .OL på Yahoo

snap = get_snapshot(ticker)
print("SNAPSHOT:")
print(snap)

prices = get_price_history(ticker, period="6mo", interval="1d")
print("\nPRICES (head):")
print(prices.head())

print("\nPRICES (tail):")
print(prices.tail())