from app.core.retry import calculate_backoff, get_celery_retry_kwargs, get_max_retries


class TestCalculateBackoff:
    def test_first_attempt_base_delay(self):
        delay = calculate_backoff(0, base_delay=2.0, jitter=False)
        assert delay == 2.0

    def test_exponential_growth(self):
        d0 = calculate_backoff(0, base_delay=2.0, jitter=False)
        d1 = calculate_backoff(1, base_delay=2.0, jitter=False)
        d2 = calculate_backoff(2, base_delay=2.0, jitter=False)
        assert d1 == d0 * 2
        assert d2 == d0 * 4

    def test_max_delay_cap(self):
        delay = calculate_backoff(20, base_delay=60.0, jitter=False, max_delay=600.0)
        assert delay == 600.0

    def test_jitter_adds_randomness(self):
        delays = {
            calculate_backoff(1, base_delay=10.0, jitter=True) for _ in range(100)
        }
        assert len(delays) > 1

    def test_jitter_within_bounds(self):
        for _ in range(100):
            delay = calculate_backoff(1, base_delay=10.0, jitter=True, max_delay=600.0)
            assert 20.0 <= delay <= 25.0


class TestGetMaxRetries:
    def test_known_task(self):
        assert get_max_retries("scrape_ebay_sold") == 3

    def test_unknown_task_uses_default(self):
        assert get_max_retries("unknown_task") == 3


class TestGetCeleryRetryKwargs:
    def test_returns_dict(self):
        kwargs = get_celery_retry_kwargs("scrape_ebay_sold")
        assert isinstance(kwargs, dict)
        assert "max_retries" in kwargs
        assert "retry_backoff" in kwargs
        assert "retry_jitter" in kwargs

    def test_max_retries_value(self):
        kwargs = get_celery_retry_kwargs("scrape_ebay_sold")
        assert kwargs["max_retries"] == 3
