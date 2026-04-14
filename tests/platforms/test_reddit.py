from unittest.mock import MagicMock, patch
from marketing_bot.platforms.reddit import RedditPublisher


@patch("marketing_bot.platforms.reddit.praw")
def test_post_to_subreddit(mock_praw):
    mock_submission = MagicMock()
    mock_submission.id = "r-abc"
    mock_submission.permalink = "/r/personalfinanceindia/comments/r-abc/title/"

    mock_subreddit = MagicMock()
    mock_subreddit.submit.return_value = mock_submission

    mock_reddit = MagicMock()
    mock_reddit.subreddit.return_value = mock_subreddit
    mock_praw.Reddit.return_value = mock_reddit

    pub = RedditPublisher(
        client_id="ci", client_secret="cs",
        username="u", password="p", user_agent="ua",
        subreddit="personalfinanceindia",
    )
    result = pub.post(("Title here", "Body content"), topic_slug="sip")

    assert result.platform == "reddit"
    assert result.post_id == "r-abc"
    assert "r-abc" in result.url
    mock_subreddit.submit.assert_called_once_with(title="Title here", selftext="Body content")
