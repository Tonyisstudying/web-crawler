from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from crawler import WebCrawler, Article
from summarizer import extract_abstract


def parse_date(value: str | None) -> datetime | None:

    if not value:
        return None

    try:
        return parser.parse(value)
    except (ValueError, TypeError, OverflowError):
        return None


def crawl_candidate_articles(
    crawler: WebCrawler,
    urls: list[str],
    workers: int = 5,
) -> list[Article]:
    articles = []
    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:
        future_map = {
            executor.submit(
                crawler.crawl_article,
                url
            ): url
            for url in urls
        }
        for future in as_completed(future_map):
            url = future_map[future]
            try:
                article = future.result()

                if article:
                    print(
                        f"[OK] {article.title}"
                    )

                    articles.append(article)

            except Exception as error:
                print(
                    f"[ERROR] {url}: {error}"
                )

    return articles


def remove_similar_articles(
    articles: list[Article],
    similarity_threshold: float = 0.65,
) -> list[Article]:

    if len(articles) <= 1:
        return articles

    documents = [
        article.title + " " + article.content
        for article in articles
    ]

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        min_df=1,
    )
    matrix = vectorizer.fit_transform(documents)
    similarity_matrix = cosine_similarity(matrix)
    selected_indices = []

    for i in range(len(articles)):
        is_duplicate = False
        for j in selected_indices:
            similarity = similarity_matrix[i][j]
            if similarity >= similarity_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            selected_indices.append(i)

    return [
        articles[i]
        for i in selected_indices
    ]


def sort_by_date(
    articles: list[Article],
) -> list[Article]:
    def sorting_key(article: Article):
        date = parse_date(article.published_time)
        if date is None:
            return datetime.min
        return date

    return sorted(
        articles,
        key=sorting_key,
        reverse=True,
    )


def generate_latest_news(
    crawler: WebCrawler,
    homepage_url: str,
    limit: int = 10,
    candidate_count: int = 40,
    similarity_threshold: float = 0.65,
) -> list[Article]:

    print("\n[1] Discovering article links...")

    links = crawler.crawl_links_from_page(
        homepage_url,
        max_links=candidate_count,
    )
    print(
        f"Found {len(links)} candidate links."
    )
    print("\n[2] Crawling articles...")
    articles = crawl_candidate_articles(
        crawler,
        links,
    )
    print(
        f"Crawled {len(articles)} valid articles."
    )
    print("\n[3] Removing similar articles...")
    unique_articles = remove_similar_articles(
        articles,
        similarity_threshold,
    )
    print(
        f"{len(unique_articles)} unique articles remain."
    )
    print("\n[4] Sorting latest news...")

    sorted_articles = sort_by_date(
        unique_articles
    )

    latest = sorted_articles[:limit]

    # Generate abstract for each article.
    for article in latest:
        article.content = article.content.strip()
        article.abstract = extract_abstract(
            article.content,
            sentence_count=3,
        )

    return latest