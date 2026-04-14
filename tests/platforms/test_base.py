from marketing_bot.platforms.base import BasePublisher, PostResult
from marketing_bot.platforms import PLATFORM_REGISTRY, register


def test_base_is_abstract():
    import pytest
    with pytest.raises(TypeError):
        BasePublisher()


def test_register_adds_to_registry():
    class Dummy(BasePublisher):
        name = "dummy"
        def post(self, content, topic_slug):
            return PostResult(post_id="d-1", url="http://x", platform="dummy")

    register(Dummy)
    assert "dummy" in PLATFORM_REGISTRY
    del PLATFORM_REGISTRY["dummy"]
