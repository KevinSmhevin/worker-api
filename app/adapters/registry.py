from app.adapters.base import BaseAdapter
from app.core.constants import Source

_ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {}


def register_adapter(source: str, adapter_cls: type[BaseAdapter]) -> None:
    _ADAPTER_REGISTRY[source] = adapter_cls


def get_adapter(source: str) -> BaseAdapter:
    adapter_cls = _ADAPTER_REGISTRY.get(source)
    if adapter_cls is None:
        raise ValueError(f"No adapter registered for source: {source}")
    return adapter_cls()


def list_adapters() -> list[str]:
    return list(_ADAPTER_REGISTRY.keys())


def _auto_register() -> None:
    """Register all built-in adapters."""
    from app.adapters.ebay.fetcher import EbayAdapter

    register_adapter(Source.EBAY, EbayAdapter)


_auto_register()
