DISCLAIMER_SHORT = "Not financial advice."
DISCLAIMER_LONG = (
    "\n\n---\nDisclaimer: This content is for educational purposes only and "
    "does not constitute financial, investment, or tax advice. Consult a "
    "SEBI-registered advisor before making investment decisions."
)

_SHORT_PLATFORMS = {"twitter"}


def append_disclaimer(content: str, platform: str) -> str:
    if platform in _SHORT_PLATFORMS:
        return f"{content}\n\n{DISCLAIMER_SHORT}"
    return f"{content}{DISCLAIMER_LONG}"
