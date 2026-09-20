#extract abstract

from __future__ import annotations

import re
from collections import Counter

import jieba


def split_sentences(text: str) -> list[str]:
    """
    Split Chinese and English text into sentences.
    """

    sentences = re.split(
        r"(?<=[。！？.!?])\s*",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 10
    ]


def tokenize(text: str) -> list[str]:
    #for Chinese text
    if re.search(r"[\u4e00-\u9fff]", text):

        words = jieba.lcut(text)

        return [
            word.strip().lower()
            for word in words
            if word.strip()
            and len(word.strip()) > 1
        ]
    #English tokenization.
    return re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )


def extract_abstract(
    text: str,
    sentence_count: int = 3,
) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""

    if len(sentences) <= sentence_count:
        return " ".join(sentences)

    #word frequency
    words = tokenize(text)

    frequency = Counter(words)

    if not frequency:
        return " ".join(
            sentences[:sentence_count]
        )

    # Normalize frequencies
    max_frequency = max(frequency.values())

    for word in frequency:
        frequency[word] /= max_frequency

    sentence_scores = []

    for index, sentence in enumerate(sentences):
        sentence_words = tokenize(sentence)
        if not sentence_words:
            continue
        score = sum(
            frequency.get(word, 0)
            for word in sentence_words
        )

        position_bonus = 1 / (1 + index)
        score += position_bonus
        sentence_scores.append(
            (index, sentence, score)
        )

    selected = sorted(
        sentence_scores,
        key=lambda item: item[2],
        reverse=True
    )[:sentence_count]

    # Keep original article order
    selected = sorted(
        selected,
        key=lambda item: item[0]
    )

    return " ".join(
        sentence
        for _, sentence, _ in selected
    )