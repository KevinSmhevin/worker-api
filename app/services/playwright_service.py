from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, Page, async_playwright

from app.core.exceptions import ScrapingError
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def get_browser(headless: bool = True) -> AsyncGenerator[Browser, None]:
    """Provide a Playwright Chromium browser instance with lifecycle management."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        try:
            yield browser
        finally:
            await browser.close()


@asynccontextmanager
async def get_page(
    headless: bool = True,
    viewport: dict | None = None,
) -> AsyncGenerator[Page, None]:
    """Provide a single browser page with a fresh context."""
    viewport = viewport or {"width": 1280, "height": 720}
    async with get_browser(headless=headless) as browser:
        context = await browser.new_context(
            viewport=viewport,
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        try:
            yield page
        finally:
            await context.close()


async def fetch_dynamic_page(
    url: str,
    *,
    wait_selector: str | None = None,
    wait_timeout: int = 30000,
) -> str:
    """Fetch a page that requires JavaScript rendering.

    Returns the full page HTML after waiting for optional selector.
    """
    try:
        async with get_page() as page:
            await page.goto(url, wait_until="networkidle", timeout=wait_timeout)

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=wait_timeout)

            html = await page.content()
            logger.info("playwright_fetch_success", url=url)
            return html

    except Exception as exc:
        logger.error("playwright_fetch_error", url=url, error=str(exc))
        raise ScrapingError(f"Playwright failed to fetch {url}") from exc
