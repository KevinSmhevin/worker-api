class WorkerAPIError(Exception):
    """Base exception for all worker-api errors."""


class RetryableError(WorkerAPIError):
    """Transient error that should be retried (timeouts, rate limits, 5xx)."""


class NonRetryableError(WorkerAPIError):
    """Permanent error that should NOT be retried (bad input, 404, auth)."""


class ScrapingError(RetryableError):
    """Error during the HTTP fetch phase of scraping."""


class ParsingError(NonRetryableError):
    """Error during HTML parsing -- indicates selector/structure change."""


class StorageError(RetryableError):
    """Error writing/reading from object storage."""


class DeduplicationError(NonRetryableError):
    """Error during deduplication check."""


class DatabaseError(RetryableError):
    """Transient database connection or query error."""
