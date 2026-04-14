import responses
from marketing_bot.newsletter.beehiiv import BeehiivClient


@responses.activate
def test_send_newsletter_creates_post():
    responses.add(
        responses.POST,
        "https://api.beehiiv.com/v2/publications/pub-1/posts",
        json={"data": {"id": "post-42"}},
        status=201,
    )
    client = BeehiivClient(api_key="k", publication_id="pub-1")
    result = client.send_newsletter(title="Weekly", body_html="<p>hi</p>")
    assert result == "post-42"
    headers = responses.calls[0].request.headers
    assert "Bearer k" in headers["Authorization"]
