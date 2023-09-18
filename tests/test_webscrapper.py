import asyncio
from pathlib import Path
import tempfile
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.webscaper.web_scraper_collector import WebScraperFactory
import pytest

from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend, WebScraperConfig


def test_webscrapper_collector():
    uri = Uri("https://asecuritysite.com/")
    resolver = CollectorResolver()
    webscrapperConfig = WebScraperConfig(website_url=uri.uri)
    collector = resolver.resolve(uri, webscrapperConfig)
    assert collector is not None


def test_fs_collector_factory():
    factory = WebScraperFactory()
    assert factory.backend() == CollectorBackend.WebScraper


def test_scrapping_data():
    uri = Uri("https://protocolstreams.xyz/")
    resolver = CollectorResolver()
    webscrapperConfig = WebScraperConfig(website_url=uri.uri)
    collector = resolver.resolve(uri, webscrapperConfig)
    assert collector is not None

    print("REached here")

    async def poll_and_print():
        print("Part 2")
        async for result in collector.poll():
            print("Hola...")
            assert not result.is_error()

    asyncio.run(poll_and_print())
