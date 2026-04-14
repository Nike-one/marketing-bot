from unittest.mock import MagicMock, patch
from marketing_bot.platforms.twitter import TwitterPublisher


@patch("marketing_bot.platforms.twitter.tweepy")
def test_post_thread_three_tweets(mock_tweepy):
    mock_client = MagicMock()
    mock_client.create_tweet.side_effect = [
        MagicMock(data={"id": "1"}),
        MagicMock(data={"id": "2"}),
        MagicMock(data={"id": "3"}),
    ]
    mock_tweepy.Client.return_value = mock_client

    pub = TwitterPublisher(
        consumer_key="ck", consumer_secret="cs",
        access_token="at", access_secret="as",
        bearer_token="bt",
    )
    result = pub.post(["t1", "t2", "t3"], topic_slug="sip")

    assert result.platform == "twitter"
    assert result.post_id == "1"
    assert "1" in result.url
    assert mock_client.create_tweet.call_count == 3
    # second tweet replies to first
    second_call = mock_client.create_tweet.call_args_list[1]
    assert second_call.kwargs["in_reply_to_tweet_id"] == "1"
