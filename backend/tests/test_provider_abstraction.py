from app.llm import get_provider
from app.llm.mock_provider import MockLLMProvider


def test_mock_provider_is_default_and_deterministic():
    p = get_provider("mock")
    assert isinstance(p, MockLLMProvider)
    a = p.complete("email", "urgent refund please")
    b = p.complete("email", "urgent refund please")
    assert a.data == b.data
    assert a.deterministic is True
