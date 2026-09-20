from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


@dataclass
class Article:
    url: str
    title: str
    content: str
    published_time: str | None = None

    def to_dict(self):
        return asdict(self)


class WebCrawler:
    def __init__(
        self,
        user_agent: str = "BigDataStudentCrawler/1.0",
        timeout: int = 15,
    ):
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })

        self.robots_cache = {}

    # Download HTML
    def fetch(self, url: str) -> str:
        response = self.session.get(
            url,
            timeout=self.timeout
        )

        response.raise_for_status()

        return response.text

    # Check robots.txt
    def allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)

        base_url = f"{parsed.scheme}://{parsed.netloc}"

        if base_url not in self.robots_cache:
            robots_url = f"{base_url}/robots.txt"
            robot_parser = RobotFileParser()
            robot_parser.set_url(robots_url)

            try:
                robot_parser.read()
            except Exception:
                pass

            self.robots_cache[base_url] = robot_parser
        robot_parser = self.robots_cache[base_url]
        return robot_parser.can_fetch(
            self.session.headers["User-Agent"],
            url
        )

    # Extract article links
    def extract_links(
        self,
        html: str,
        base_url: str,
        same_domain_only: bool = True,
    ) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(base_url).netloc
        links = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if not href:
                continue
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            if parsed.scheme not in ("http", "https"):
                continue
            if same_domain_only and parsed.netloc != base_domain:
                continue

            # Ignore files
            ignored_extensions = (
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".pdf",
                ".zip",
                ".mp4",
            )

            if parsed.path.lower().endswith(ignored_extensions):
                continue

            clean_url = (
                f"{parsed.scheme}://"
                f"{parsed.netloc}"
                f"{parsed.path}"
            )

            if clean_url not in links:
                links.append(clean_url)

        return links

    # Extract page title
    def extract_title(self, soup: BeautifulSoup) -> str:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(" ", strip=True)
            if title:
                return title
        og_title = soup.find(
            "meta",
            property="og:title"
        )

        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        title_tag = soup.find("title")

        if title_tag:
            return title_tag.get_text(" ", strip=True)

        return ""

    # Extract publication time
    def extract_time(self, soup: BeautifulSoup) -> str | None:
        time_tag = soup.find("time")
        if time_tag:
            datetime_value = time_tag.get("datetime")
            if datetime_value:
                return datetime_value.strip()
            text = time_tag.get_text(" ", strip=True)
            if text:
                return text

        # Common metadata fields
        meta_names = [
            "article:published_time",
            "publishdate",
            "pubdate",
            "date",
        ]

        for name in meta_names:

            tag = soup.find("meta", attrs={"name": name})

            if tag and tag.get("content"):
                return tag["content"].strip()

        # OpenGraph publication time
        tag = soup.find(
            "meta",
            property="article:published_time"
        )

        if tag and tag.get("content"):
            return tag["content"].strip()

        return None

    # Extract article text
    def extract_content(self, soup: BeautifulSoup) -> str:
        # Remove elements that normally don't contain
        # article text.
        for tag in soup([
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
        ]):
            tag.decompose()
        article_tag = soup.find("article")
        if article_tag:
            paragraphs = article_tag.find_all("p")
            text = "\n".join(
                p.get_text(" ", strip=True)
                for p in paragraphs
            )
            if len(text) >= 100:
                return text

        # Fallback: collect all paragraphs
        paragraphs = soup.find_all("p")
        texts = []
        for p in paragraphs:
            text = p.get_text(" ", strip=True)
            if len(text) >= 30:
                texts.append(text)
        return "\n".join(texts)

    # Crawl one page
    def crawl_article(self, url: str) -> Article | None:
        if not self.allowed_by_robots(url):
            print(f"[ROBOTS] Skipping: {url}")
            return None
        try:
            html = self.fetch(url)
        except requests.RequestException as error:
            print(f"[ERROR] {url}: {error}")
            return None

        soup = BeautifulSoup(html, "html.parser")

        title = self.extract_title(soup)
        content = self.extract_content(soup)
        published_time = self.extract_time(soup)

        if not title:
            return None

        if len(content) < 100:
            return None

        return Article(
            url=url,
            title=title,
            content=content,
            published_time=published_time,
        )

    # Crawl homepage and discover links
    def crawl_links_from_page(
        self,
        url: str,
        max_links: int = 30,
    ) -> list[str]:
        if not self.allowed_by_robots(url):
            return []
        try:
            html = self.fetch(url)
        except requests.RequestException as error:
            print(f"[ERROR] {error}")
            return []
        links = self.extract_links(
            html,
            url,
            same_domain_only=True,
        )
        return links[:max_links]