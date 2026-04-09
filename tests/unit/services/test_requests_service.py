from app.services.requests_service import USER_AGENTS, _random_user_agent


class TestRandomUserAgent:
    def test_returns_string(self):
        ua = _random_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 0

    def test_returns_from_list(self):
        ua = _random_user_agent()
        assert ua in USER_AGENTS

    def test_user_agents_not_empty(self):
        assert len(USER_AGENTS) > 0
