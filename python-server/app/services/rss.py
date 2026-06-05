import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
from html.parser import HTMLParser


NAVER_RSS_URL = "https://rss.blog.naver.com/{blog_id}.xml"


class _StripHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts).strip()


def _strip_html(html: str) -> str:
    parser = _StripHTML()
    parser.feed(html or "")
    return parser.get_text()


def _parse_date(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return datetime.strptime(raw.strip(), fmt).isoformat()
        except ValueError:
            continue
    return raw.strip()


async def fetch_naver_blog(blog_id: str) -> dict:
    url = NAVER_RSS_URL.format(blog_id=blog_id)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, follow_redirects=True)

    if resp.status_code == 404:
        raise ValueError(f"블로그를 찾을 수 없습니다: {blog_id}")
    if resp.status_code != 200:
        raise RuntimeError(f"RSS 요청 실패: {resp.status_code}")

    root = ET.fromstring(resp.text)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("RSS 형식 오류: channel 요소가 없습니다.")

    def text(tag: str) -> Optional[str]:
        el = channel.find(tag)
        return el.text.strip() if el is not None and el.text else None

    def item_text(el, tag: str) -> Optional[str]:
        child = el.find(tag)
        return child.text.strip() if child is not None and child.text else None

    posts = []
    for item in channel.findall("item"):
        raw_desc = item_text(item, "description") or ""
        posts.append({
            "title": item_text(item, "title"),
            "link": item_text(item, "link"),
            "description": _strip_html(raw_desc)[:300],
            "pub_date": _parse_date(item_text(item, "pubDate")),
            "category": item_text(item, "category"),
        })

    return {
        "blog_id": blog_id,
        "blog_title": text("title"),
        "blog_description": text("description"),
        "blog_url": text("link"),
        "total_posts": len(posts),
        "posts": posts,
    }
