import asyncio
import random

import httpx

from app.core.config import get_settings
from app.core.exceptions import ScrapingError
from app.core.logging import get_logger
from app.core.retry import calculate_backoff

logger = get_logger(__name__)

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) "
        "Gecko/20100101 Firefox/126.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.5 Safari/605.1.15"
    ),
]


def _random_user_agent() -> str:
    return random.choice(USER_AGENTS)


async def fetch_url(
    url: str,
    *,
    method: str = "GET",
    headers: dict | None = None,
    params: dict | None = None,
    max_retries: int | None = None,
    timeout: int | None = None,
) -> str:
    """Fetch a URL with retry, rate limiting, and User-Agent rotation.

    Returns the response body as text.
    Raises ScrapingError on persistent failure.
    """
    settings = get_settings()
    max_retries = max_retries or settings.max_retries
    timeout = timeout or settings.default_request_timeout

    default_headers = {
        "User-Agent": _random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if headers:
        default_headers.update(headers)

    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(
                timeout=timeout, follow_redirects=True
            ) as client:
                response = await client.request(
                    method, url, headers=default_headers, params=params
                )
                response.raise_for_status()

                logger.info(
                    "fetch_success",
                    url=url,
                    status_code=response.status_code,
                    attempt=attempt + 1,
                )
                return response.text

        except httpx.TimeoutException as exc:
            last_error = exc
            logger.warning("fetch_timeout", url=url, attempt=attempt + 1)
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code in (429, 500, 502, 503, 504):
                logger.warning(
                    "fetch_retryable_status",
                    url=url,
                    status_code=exc.response.status_code,
                    attempt=attempt + 1,
                )
            else:
                raise ScrapingError(
                    f"Non-retryable HTTP {exc.response.status_code} for {url}"
                ) from exc
        except httpx.RequestError as exc:
            last_error = exc
            logger.warning("fetch_request_error", url=url, attempt=attempt + 1)

        if attempt < max_retries:
            delay = calculate_backoff(attempt, base_delay=settings.rate_limit_delay)
            logger.info("fetch_retry_backoff", url=url, delay=delay)
            await asyncio.sleep(delay)

    raise ScrapingError(
        f"Failed to fetch {url} after {max_retries + 1} attempts"
    ) from last_error
