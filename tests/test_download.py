from multibagger.core.downloader import MarketDataDownloader

downloader = MarketDataDownloader()

downloader.download_universe(
    "test",
    force=True
)