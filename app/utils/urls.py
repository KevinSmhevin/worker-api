from urllib.parse import urlencode, urljoin, urlparse


def build_url(base: str, path: str = "", params: dict | None = None) -> str:
    url = urljoin(base, path)
    if params:
        url = f"{url}?{urlencode(params)}"
    return url


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc
