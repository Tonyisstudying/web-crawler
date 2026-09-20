Big Data Web Crawler

A lightweight Python-based Big Data project that crawls a target news website, extracts article information, generates extractive abstracts, detects highly similar news articles, and produces a list of the 10 latest unique news articles.

The project is designed for a Big Data / Data Mining / NLP course project and emphasizes a clear end-to-end pipeline rather than a complicated production backend.

1. Project Overview

Problem

News websites can contain many articles covering the same event. A simple crawler may therefore return a list containing several near-duplicate articles.

This project solves three related tasks:

Web Crawling — collect article links and extract article metadata/content from a specified website.

Abstract Extraction — generate a short extractive summary from each article.

Latest Unique News Selection — rank articles by publication time and remove highly similar articles so that only one representative article from a similar-news group is retained.

High-Level Pipeline

                  Target News Website
                          |
                          v
                   Web Crawler
                          |
             +------------+------------+
             |                         |
             v                         v
       Article Metadata            Article Text
             |                         |
             +------------+------------+
                          |
                          v
                  Text Processing
                          |
             +------------+------------+
             |                         |
             v                         v
       Abstract Extraction       TF-IDF Vectorization
                                       |
                                       v
                              Cosine Similarity
                                       |
                                       v
                              Similarity Filtering
                                       |
                                       v
                              Sort by Date/Time
                                       |
                                       v
                              Latest 10 Unique News
                                       |
                                       v
                                data/news.json

2. Main Requirements

Requirement 1 — Simple Web Crawler

The crawler accepts a target webpage and attempts to discover article URLs on the same domain.

For each valid article, it extracts:

Article URL

Title

Publication time, when available

Main article text

The implementation uses requests for HTTP requests and BeautifulSoup for HTML parsing.

Requirement 2 — Abstract Extraction

The project uses an extractive summarization approach.

The summarizer:

Splits the article into sentences.

Tokenizes the text.

Calculates word/term frequency.

Scores sentences according to the importance of their terms.

Selects the highest-scoring sentences.

Restores the original sentence order to form the abstract.

This approach does not generate new text with an LLM; it selects representative sentences from the original article.

Requirement 3 — 10 Latest Non-Similar News Articles

The system crawls a larger candidate set, then:

Converts article text into TF-IDF vectors.

Computes pairwise cosine similarity.

Removes articles whose similarity is above a configurable threshold.

Sorts the remaining articles by publication time.

Keeps the latest 10 articles.

The default similarity threshold is 0.65, but this can be adjusted depending on the target website and dataset.

3. Technologies

Technology

Purpose

Python 3

Main programming language

Requests

HTTP requests and page downloading

BeautifulSoup 4

HTML parsing and information extraction

jieba

Chinese word segmentation

scikit-learn

TF-IDF and cosine similarity

python-dateutil

Publication-date parsing

argparse

Command-line interface

JSON

Result storage

4. Project Structure

big_data_project/
│
├── main.py                  # CLI entry point
├── crawler.py               # Web crawling and article extraction
├── summarizer.py            # Extractive abstract generation
├── news_processor.py        # Similarity filtering and news selection
├── requirements.txt         # Python dependencies
│
└── data/
    └── news.json            # Generated news results

Module Responsibilities

crawler.py

Responsible for:

Sending HTTP requests

Checking robots.txt

Discovering article links

Extracting article titles

Extracting publication times

Extracting article text

Main class:

WebCrawler

Main data structure:

Article

summarizer.py

Responsible for:

Sentence segmentation

Tokenization

Term-frequency calculation

Sentence scoring

Extractive abstract generation

Main function:

extract_abstract()

news_processor.py

Responsible for:

Crawling multiple candidate articles

Parallel crawling with ThreadPoolExecutor

Parsing publication dates

TF-IDF vectorization

Cosine similarity calculation

Similar-news filtering

Sorting by publication time

Main function:

generate_latest_news()

main.py

Provides the command-line interface and connects all components into the complete pipeline.

5. Installation

Step 1 — Clone the repository

git clone <YOUR_REPOSITORY_URL>
cd big_data_project

Step 2 — Create a virtual environment

Windows

python -m venv .venv
.venv\Scripts\activate

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

Step 3 — Install dependencies

pip install -r requirements.txt

6. Usage

The application exposes three commands: crawl, abstract, and news.

6.1 Crawl a Webpage

python main.py crawl --url https://example.com/article

This prints the extracted title, publication time, and article content.

6.2 Extract an Abstract

python main.py abstract --url https://example.com/article

The system prints a short extractive abstract composed of important sentences from the article.

6.3 Generate the Latest 10 Unique News Articles

python main.py news --url https://example.com/ --limit 10

The crawler will:

Discover article links
        ↓
Crawl candidate articles
        ↓
Extract article information
        ↓
Remove highly similar articles
        ↓
Sort by publication time
        ↓
Select the latest 10
        ↓
Generate abstracts
        ↓
Save data/news.json

7. Example Output

Example terminal output:

[1] Discovering article links...
Found 40 candidate links.

[2] Crawling articles...
[OK] Example news article 1
[OK] Example news article 2
[OK] Example news article 3
...

Crawled 28 valid articles.

[3] Removing similar articles...
20 unique articles remain.

[4] Sorting latest news...

========== LATEST NEWS ==========

======================================================================
1. Example News Title
Date: 2026-09-20T10:30:00+08:00
URL: https://example.com/news/1

Abstract:
Example article summary...

The generated JSON is stored in:

data/news.json

Example structure:

[
  {
    "title": "Example News Title",
    "url": "https://example.com/news/1",
    "published_time": "2026-09-20T10:30:00+08:00",
    "abstract": "Example article abstract..."
  }
]

8. Similar-News Detection

The duplicate-removal stage is based on TF-IDF + cosine similarity.

TF-IDF

TF-IDF converts each article into a numerical representation based on how important its terms are within the collection of documents.

Conceptually:

Article A → TF-IDF vector A
Article B → TF-IDF vector B
Article C → TF-IDF vector C

Cosine Similarity

For two article vectors A and B:

cosine_similarity(A, B)
    = (A · B) / (||A|| × ||B||)

The result is used as a similarity score.

If:

similarity >= threshold

then the later article in the filtering sequence is treated as sufficiently similar to an already selected article and is not kept as a separate result.

Current Default

similarity_threshold = 0.65

This is a heuristic parameter, not a universal definition of duplicate news. It should be validated against the target website and the course dataset.

9. Why Character n-Gram TF-IDF?

The similarity module uses:

TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 5),
)

Character n-grams are useful for multilingual or Chinese-heavy news because they do not depend completely on perfect word segmentation.

For example, related strings can still share character-level patterns even when tokenization differs slightly.

This makes the approach a practical baseline for the course project.

10. Abstract Extraction Method

The project uses an extractive method rather than an abstractive language model.

For every article:

Raw article
    ↓
Sentence segmentation
    ↓
Tokenization
    ↓
Word frequency
    ↓
Sentence scoring
    ↓
Top N sentences
    ↓
Original sentence order
    ↓
Abstract

Advantages of this approach for the project:

No external API is required.

Results are deterministic enough for a baseline implementation.

It is easy to explain in a course presentation.

It demonstrates NLP concepts without introducing a large language model dependency.

11. Design Considerations

Robots.txt

The crawler checks the site's robots.txt before crawling an URL. A website may still prohibit automated access through its terms of service or other technical restrictions, so the project should only be used with websites that permit the intended crawling activity.

Website Structure

Different websites use different HTML structures. The crawler therefore uses several fallbacks such as:

<h1>
<meta property="og:title">
<title>

for titles and several common metadata locations for publication time.

Article-body extraction also prefers <article> and falls back to paragraphs when needed.

Anti-Bot and JavaScript Rendering

This project is intentionally a simple crawler. It does not attempt to bypass CAPTCHAs, anti-bot systems, login restrictions, or access controls. Sites whose content is rendered primarily through JavaScript may require a browser automation tool and site-specific handling.

12. Limitations

This is a course-oriented baseline rather than a production crawler.

Current limitations include:

Article extraction depends on the HTML structure of the target site.

Publication dates may be missing or ambiguous.

Similarity threshold selection is heuristic.

TF-IDF does not understand semantic meaning as deeply as modern embedding models.

The crawler discovers links from a page rather than maintaining a large distributed crawl frontier.

The summarizer is extractive and may produce an imperfect summary.

Very JavaScript-heavy websites may not expose the article content directly in the downloaded HTML.

13. Possible Improvements

The baseline can be extended into a more advanced Big Data system.

Improved NLP

Replace TF-IDF with multilingual sentence/document embeddings:

Article
   ↓
Embedding Model
   ↓
Vector Representation
   ↓
Cosine Similarity
   ↓
Semantic Deduplication

Better Summarization

Possible alternatives include:

TextRank

Transformer-based summarization

BART / mT5-style summarization

LLM-based summarization

Persistent Storage

Instead of writing only JSON, store collected data in:

MySQL / PostgreSQL
        or
MongoDB
        or
Elasticsearch

Distributed Processing

For a stronger Big Data implementation, the processing stage can be expanded to:

Web Crawlers
      ↓
Message Queue
      ↓
Data Lake / HDFS
      ↓
Spark
      ↓
NLP + Similarity Processing
      ↓
Database / Data Warehouse
      ↓
Dashboard

Possible technologies:

Apache Kafka

Apache Spark

HDFS

Elasticsearch

Airflow

Docker

These additions are optional; they are not required for the basic three requirements.

14. Suggested Evaluation

To demonstrate that the project works, evaluate each requirement separately.

Crawler Evaluation

Measure:

Number of discovered links

Number of successfully crawled articles

Percentage of articles with valid titles

Percentage of articles with publication times

Percentage of articles with usable content

Abstract Evaluation

For a small manually labeled sample, compare generated abstracts with manually selected key sentences.

Possible measurements include:

Human relevance assessment

ROUGE, when reference summaries are available

Similarity Evaluation

Create a small test set containing:

Group A → same event / highly similar reports
Group B → related but meaningfully different articles
Group C → unrelated articles

Then test different thresholds, for example:

0.50
0.60
0.65
0.70
0.80

and examine false duplicate removals versus missed duplicates.

15. Recommended Demonstration Flow

For a course presentation, demonstrate the system in this order:

Step 1 — Input

Provide the homepage URL:

https://<target-news-site>/

Step 2 — Crawling

Show that the crawler discovers multiple article URLs.

Step 3 — Extraction

Show one article's:

Title
Publication Time
Content

Step 4 — Abstract

Show the original article followed by its extracted abstract.

Step 5 — Similarity

Show two similar articles and their cosine similarity score conceptually or through an experiment.

Step 6 — Final Result

Show the final list of up to 10 unique latest articles.

Step 7 — Stored Dataset

Open:

data/news.json

and explain the fields.

16. Learning Objectives Demonstrated

This project combines several important concepts:

Web Scraping
     +
HTML Parsing
     +
Data Cleaning
     +
Text Processing
     +
Chinese NLP
     +
TF-IDF
     +
Cosine Similarity
     +
Deduplication
     +
Data Storage
     =
End-to-End Big Data / NLP Pipeline

The project demonstrates how unstructured web data can be transformed into a structured and filtered dataset suitable for further analysis.

17. License / Academic Use

This repository is intended for educational and academic project work. Before crawling a third-party website, review that site's terms of service, robots directives, and applicable laws or institutional policies.