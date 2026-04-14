import requests


class BeehiivClient:
    BASE = "https://api.beehiiv.com/v2"

    def __init__(self, api_key: str, publication_id: str):
        self.api_key = api_key
        self.publication_id = publication_id

    def send_newsletter(self, title: str, body_html: str) -> str:
        resp = requests.post(
            f"{self.BASE}/publications/{self.publication_id}/posts",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "title": title,
                "body_content": body_html,
                "status": "confirmed",
                "content_tags": ["finance", "india"],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["data"]["id"]
