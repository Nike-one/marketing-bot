import responses
from marketing_bot.platforms.linkedin import LinkedInPublisher


@responses.activate
def test_post_to_linkedin():
    responses.add(
        responses.POST,
        "https://api.linkedin.com/v2/ugcPosts",
        json={"id": "urn:li:share:abc123"},
        status=201,
        headers={"x-restli-id": "urn:li:share:abc123"},
    )
    pub = LinkedInPublisher(
        access_token="tok",
        person_urn="urn:li:person:xyz",
    )
    result = pub.post("hello world", topic_slug="sip")
    assert result.post_id == "urn:li:share:abc123"
    assert result.platform == "linkedin"
    assert "abc123" in result.url
    body = responses.calls[0].request.body
    if isinstance(body, bytes):
        assert b"hello world" in body
    else:
        assert "hello world" in body
