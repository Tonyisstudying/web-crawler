from __future__ import annotations

import argparse
import json
from pathlib import Path

from crawler import WebCrawler
from summarizer import extract_abstract
from news_processor import generate_latest_news


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def save_news(news):
    output = []
    for article in news:
        output.append({
            "title": article.title,
            "url": article.url,
            "published_time": article.published_time,
            "abstract": getattr(
                article,
                "abstract",
                "",
            ),
        })
    output_path = DATA_DIR / "news.json"
    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )
    print(
        f"\nSaved results to {output_path}"
    )


def crawl_command(url: str):
    crawler = WebCrawler()
    article = crawler.crawl_article(url)
    if not article:
        print("Unable to extract article.")
        return

    print("\n========== ARTICLE ==========")

    print("\nTitle:")
    print(article.title)

    print("\nPublished:")
    print(article.published_time)

    print("\nContent:")
    print(article.content[:2000])


def abstract_command(url: str):
    crawler = WebCrawler()
    article = crawler.crawl_article(url)
    if not article:
        print("Unable to extract article.")
        return

    abstract = extract_abstract(
        article.content,
        sentence_count=3,
    )

    print("\n========== ABSTRACT ==========")
    print(abstract)


def news_command(
    url: str,
    limit: int,
):
    crawler = WebCrawler()
    news = generate_latest_news(
        crawler=crawler,
        homepage_url=url,
        limit=limit,
        candidate_count=40,
        similarity_threshold=0.65,
    )
    print("\n\n========== LATEST NEWS ==========\n")

    for index, article in enumerate(
        news,
        start=1,
    ):

        print("=" * 70)
        print(f"{index}. {article.title}")
        print(
            f"Date: {article.published_time}"
        )
        print(
            f"URL: {article.url}"
        )
        print("\nAbstract:")
        print(
            getattr(
                article,
                "abstract",
                "",
            )
        )
        print()

    save_news(news)

def main():
    parser = argparse.ArgumentParser(
        description="Big Data Web Crawler Project"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Crawl command
    crawl_parser = subparsers.add_parser(
        "crawl",
        help="Crawl one webpage",
    )
    crawl_parser.add_argument(
        "--url",
        required=True,
    )

    # Abstract command

    abstract_parser = subparsers.add_parser(
        "abstract",
        help="Extract article abstract",
    )
    abstract_parser.add_argument(
        "--url",
        required=True,
    )

    # News command

    news_parser = subparsers.add_parser(
        "news",
        help="Get latest unique news",
    )
    news_parser.add_argument(
        "--url",
        required=True,
    )
    news_parser.add_argument(
        "--limit",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    if args.command == "crawl":
        crawl_command(args.url)
    elif args.command == "abstract":
        abstract_command(args.url)
    elif args.command == "news":
        news_command(
            args.url,
            args.limit,
        )

if __name__ == "__main__":
    main()