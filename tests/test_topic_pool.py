import json
from pathlib import Path


def test_topic_pool_loads():
    path = Path(__file__).parent.parent / "topic_pool.json"
    data = json.loads(path.read_text())
    assert isinstance(data, list)
    assert len(data) >= 50
    for entry in data:
        assert "slug" in entry
        assert "title" in entry
        assert "hook" in entry
        assert "category" in entry
    slugs = [e["slug"] for e in data]
    assert len(slugs) == len(set(slugs)), "slugs must be unique"
