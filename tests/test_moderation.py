from marketing_bot.moderation import append_disclaimer, DISCLAIMER_SHORT, DISCLAIMER_LONG


def test_short_disclaimer_for_twitter():
    out = append_disclaimer("SIP is good", platform="twitter")
    assert DISCLAIMER_SHORT in out
    assert out.startswith("SIP is good")


def test_long_disclaimer_for_newsletter():
    out = append_disclaimer("Long article body", platform="newsletter")
    assert DISCLAIMER_LONG in out


def test_long_disclaimer_for_linkedin():
    out = append_disclaimer("Professional post", platform="linkedin")
    assert DISCLAIMER_LONG in out


def test_long_disclaimer_for_reddit():
    out = append_disclaimer("Reddit value post", platform="reddit")
    assert DISCLAIMER_LONG in out
