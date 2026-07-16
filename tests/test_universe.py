from multibagger.core.universe_loader import UniverseLoader

loader = UniverseLoader("test")

symbols = loader.load()

print(f"Loaded {len(symbols)} symbols")

print(symbols[:20])