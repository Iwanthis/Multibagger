from atlas.core.data_loader import DataLoader

loader = DataLoader("nifty500")

stocks = loader.load()

print("=" * 60)
print(f"Loaded {len(stocks)} stocks")
print("=" * 60)

for symbol, df in list(stocks.items())[:10]:
    print(f"{symbol:15} {len(df):5} rows")