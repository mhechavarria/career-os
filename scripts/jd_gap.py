#!/usr/bin/env python3
"""
jd_gap.py — keyword gap analyzer for Career OS CVs

Usage:
    python3 scripts/jd_gap.py <jd.txt> <cv.md>

Outputs:
    MISSING  — keywords in JD but not found in CV (highest priority to fix)
    WEAK     — keywords in JD 2+ times but only once in CV
    PRESENT  — keywords confirmed in both
"""

import argparse
import re
import sys
from pathlib import Path
from collections import Counter


STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "can",
    "not",
    "its",
    "we",
    "you",
    "they",
    "their",
    "our",
    "your",
    "it",
    "he",
    "she",
    "who",
    "what",
    "which",
    "that",
    "this",
    "these",
    "those",
    "when",
    "where",
    "how",
    "if",
    "all",
    "any",
    "both",
    "each",
    "more",
    "most",
    "other",
    "some",
    "than",
    "then",
    "so",
    "up",
    "out",
    "into",
    "about",
    "over",
    "after",
    "before",
    "through",
    "during",
    "without",
    "within",
    "work",
    "working",
    "team",
    "experience",
    "strong",
    "knowledge",
    "skills",
    "ability",
    "understand",
    "develop",
    "build",
    "use",
    "using",
    "used",
    "years",
    "new",
    "also",
    "well",
    "must",
    "need",
    "required",
    "preferred",
    "great",
    "good",
    "excellent",
    "help",
    "make",
    "own",
    "role",
    "position",
    "company",
    "product",
    "platform",
    "solutions",
    "based",
    "across",
    "get",
    "set",
    "run",
    "take",
    "ensure",
    "provide",
    "support",
    "manage",
    "maintain",
    "contribute",
    "create",
    "include",
    "including",
    "such",
    "like",
    "drive",
    "design",
    "implement",
    "write",
    "test",
    "review",
    "background",
    "plus",
    "bonus",
    "ideal",
    "nice",
    "hire",
    "hiring",
    "join",
    "apply",
    "candidate",
    "applicant",
}

# Curated multi-word phrases detected as single units (longest first).
# All entries are lowercased — matched against lowercased text, so they
# catch both "Kafka" and "kafka", "GraphQL" and "graphql", etc.
TECH_PHRASES = [
    # AI / LLM
    "large language models",
    "large language model",
    "retrieval augmented generation",
    "rag architecture",
    "prompt engineering",
    "vector databases",
    "vector database",
    "agentic workflows",
    "agentic engineering",
    "ai-augmented",
    "anthropic claude",
    "github copilot",
    # Architecture
    "event-driven architecture",
    "event driven architecture",
    "distributed systems",
    "distributed computing",
    "infrastructure as code",
    "infrastructure-as-code",
    "system design",
    "high availability",
    "fault tolerance",
    "event sourcing",
    "saga pattern",
    "blue-green deployment",
    "canary deployment",
    "zero downtime deployment",
    "monorepo",
    "mono-repo",
    # Cloud — AWS
    "aws cdk",
    "aws lambda",
    "aws ecs",
    "aws rds",
    "aws eventbridge",
    "aws dynamodb",
    "aws cloudwatch",
    "aws codepipeline",
    "aws codebuild",
    "aws iot core",
    "aws api gateway",
    "aws bedrock",
    "aws govcloud",
    "fedramp high",
    "fedramp",
    # Cloud — GCP
    "google kubernetes engine",
    "google cloud platform",
    "google cloud",
    # Containers / orchestration
    "kubernetes",
    "k8s",
    # DevOps / CI-CD
    "github actions",
    "gh actions",
    "gitlab ci",
    "gitlab ci/cd",
    "continuous integration",
    "continuous delivery",
    "continuous deployment",
    "docker compose",
    "helm charts",
    "ci/cd",
    # APIs / Auth / Protocols
    "rest apis",
    "rest api",
    "oauth 2.0",
    "oauth2",
    "api gateway",
    "api design",
    "graphql",
    "grpc",
    "websocket",
    "websockets",
    "openapi",
    "swagger",
    # Databases / Messaging
    "sql server",
    "message queue",
    "message broker",
    "apache kafka",
    "kafka streams",
    "pub/sub",
    "rabbitmq",
    "postgresql",
    "postgres",
    "dynamodb",
    "mongodb",
    "elasticsearch",
    # Observability
    "distributed tracing",
    "structured logging",
    "new relic",
    "open telemetry",
    # Testing
    "end-to-end testing",
    "integration testing",
    "unit testing",
    "test driven development",
    "tdd",
    # JS / TS ecosystem
    "node.js",
    "nodejs",
    "typeorm",
    "prisma orm",
    "prisma",
    # Java ecosystem
    "spring boot",
    # Security / Compliance
    "soc 2",
    "govcloud",
    # Work style
    "remote-first",
    "fully remote",
    "async-first",
    "asynchronous communication",
    # Single-word tech terms missed by the CamelCase regex
    # (kafka, redis, nginx, etc. don't follow CamelCase or ALL_CAPS)
    # "golang" is unambiguous; the bare "Go" language token is detected
    # separately in extract_tech_tokens() (capitalized only) so it doesn't
    # match ordinary English like "go to market" / "go deep".
    "golang",
    "kafka",
    "redis",
    "nginx",
    "helm",
    "grafana",
    "prometheus",
    "datadog",
    "sentry",
    "jest",
    "vitest",
    "mocha",
    "pytest",
    "terraform",
    "ansible",
    "sequelize",
    "celery",
    "airflow",
]

# Variant spellings folded into a single canonical term, so a JD and CV that
# spell the same technology differently still count as a match. Both sides of
# each pair must also appear in TECH_PHRASES to be detected in the first place.
SYNONYMS = {
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "gh actions": "github actions",
    "nodejs": "node.js",
    "oauth2": "oauth 2.0",
    "mono-repo": "monorepo",
    "event driven architecture": "event-driven architecture",
    "infrastructure-as-code": "infrastructure as code",
    "golang": "go",
}

# Language names that are also common English words ("Go", "Rust") are detected
# as capitalized standalone tokens rather than via TECH_PHRASES, so ordinary
# prose ("go to market", "rust never sleeps", "trust") isn't miscounted as the
# language. This is the extensible home for that class of term — the curated
# TECH_PHRASES list can't safely hold a bare common word, so add new ones here.
CAPITALIZED_LANG_TOKENS = {
    "go": r"\bGo\b(?!-)(?!\s+(?:to|deep|above|beyond|live|the|further|all))",
    "rust": r"\bRust\b(?!\s+Belt)",
}


def strip_markdown(text: str) -> str:
    text = re.sub(r"^---[\s\S]*?---\n", "", text)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"[#*`>|~_]", " ", text)
    return text


def extract_tech_tokens(text: str) -> Counter:
    counts: Counter = Counter()
    norm = text.lower()

    # Multi-word phrases (longest match first to avoid double-counting)
    for phrase in sorted(TECH_PHRASES, key=len, reverse=True):
        count = len(re.findall(r"\b" + re.escape(phrase) + r"\b", norm))
        if count > 0:
            counts[phrase] += count
            # Blank out matched phrases so sub-terms don't double-count
            norm = re.sub(r"\b" + re.escape(phrase) + r"\b", " ", norm)

    # Language names that are also common English words ("Go", "Rust"):
    # capitalized standalone tokens only (see CAPITALIZED_LANG_TOKENS), so prose
    # like "go to market" / "trust" isn't miscounted. "golang" (in TECH_PHRASES)
    # folds into "go" via SYNONYMS.
    for canon, pattern in CAPITALIZED_LANG_TOKENS.items():
        n = len(re.findall(pattern, text))
        if n:
            counts[canon] += n

    # Tech-formatted single tokens from original text
    tech_token = re.compile(
        r"\b("
        r"[A-Z][A-Za-z0-9]*(?:\.[A-Za-z0-9]+)+"  # Node.js, DynamoDB
        r"|[A-Z]{2,}(?:/[A-Z]{2,})*"  # AWS, GCP, CI/CD, REST
        r"|[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+"  # TypeScript, PostgreSQL, DynamoDB
        r"|[a-z]+\+\+"  # c++
        r"|[A-Za-z]+#"  # C#
        r")\b"
    )
    for match in tech_token.finditer(text):
        token = match.group(1).lower()
        if token not in STOP_WORDS and len(token) >= 2:
            counts[token] += 1

    # Fold variant spellings into their canonical term
    folded: Counter = Counter()
    for term, n in counts.items():
        folded[SYNONYMS.get(term, term)] += n
    return folded


def _variants_of(term: str) -> list:
    """A canonical term plus any variant spellings that fold into it."""
    return [term] + [variant for variant, canon in SYNONYMS.items() if canon == term]


def count_in_text(term: str, text: str) -> int:
    text_lower = text.lower()
    total = 0
    for variant in _variants_of(term):
        if variant in CAPITALIZED_LANG_TOKENS:
            # Bare common-word language names ("Go", "Rust") are matched with the
            # same capitalized, context-guarded pattern used for JD extraction —
            # against original-case text — so CV prose ("Rust Belt", "go to market")
            # isn't miscounted as covering the language. A lowercased \bword\b here
            # would falsely mark such a CV as covering the keyword and drop a real
            # gap from the report.
            total += len(re.findall(CAPITALIZED_LANG_TOKENS[variant], text))
        else:
            total += len(re.findall(r"\b" + re.escape(variant) + r"\b", text_lower))
    return total


def score(missing: list, weak: list, present: list) -> int:
    """Keyword coverage %: PRESENT=full weight, WEAK=half weight, MISSING=zero. 0–100.

    This is a JD-frequency bag-of-words overlap, not a fit verdict — a high number
    means the CV echoes the JD's vocabulary, nothing more. Don't let it drive
    apply/skip decisions on its own.
    """
    total = (
        sum(f for _, f in missing)
        + sum(f for _, f, _ in weak)
        + sum(f for _, f, _ in present)
    )
    if total == 0:
        return 0
    earned = sum(f for _, f, _ in present) + sum(f for _, f, _ in weak) * 0.5
    return round(earned / total * 100)


def run(jd_path: str, cv_path: str) -> int:
    """Run gap analysis and return the keyword coverage % (0–100)."""
    jd_text = Path(jd_path).read_text(encoding="utf-8")
    cv_raw = Path(cv_path).read_text(encoding="utf-8")
    cv_text = strip_markdown(cv_raw)

    jd_counts = extract_tech_tokens(jd_text)

    missing, weak, present = [], [], []

    for term, jd_freq in sorted(jd_counts.items(), key=lambda x: -x[1]):
        cv_freq = count_in_text(term, cv_text)
        if cv_freq == 0:
            missing.append((term, jd_freq))
        elif jd_freq >= 2 and cv_freq == 1:
            weak.append((term, jd_freq, cv_freq))
        else:
            present.append((term, jd_freq, cv_freq))

    coverage = score(missing, weak, present)

    print("\n=== JD Keyword Gap Report ===")
    print(f"  JD : {jd_path}")
    print(f"  CV : {cv_path}")
    print(
        f"  Keyword coverage : {coverage}%  (vocabulary overlap, not a fit verdict)\n"
    )

    if missing:
        print(f"MISSING ({len(missing)}) — not in CV, address before sending:")
        for term, freq in missing[:30]:
            priority = "!!" if freq >= 3 else " !"
            print(f"  {priority} [{freq}x in JD]  {term}")
    else:
        print("MISSING: none — full coverage!")

    if weak:
        print(f"\nWEAK ({len(weak)}) — in JD {chr(8805)}2x but only once in CV:")
        for term, jd_f, cv_f in weak[:15]:
            print(f"      [{jd_f}x JD / {cv_f}x CV]  {term}")

    if present:
        print(f"\nPRESENT ({len(present)}) — confirmed in both:")
        for term, jd_f, cv_f in present[:30]:
            print(f"      [{jd_f}x JD / {cv_f}x CV]  {term}")

    print()
    return coverage


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Keyword-coverage gap analysis between a job description and a CV."
    )
    parser.add_argument("jd", help="Path to the JD text file (e.g. jds/role.txt)")
    parser.add_argument("cv", help="Path to the CV markdown file (e.g. cv/master.md)")
    args = parser.parse_args()

    # Fail with a clear message instead of an unhandled traceback (matches
    # generate_cv.py). run() itself still raises for library callers.
    for label, path in (("JD", args.jd), ("CV", args.cv)):
        if not Path(path).exists():
            print(f"Error: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    run(args.jd, args.cv)


if __name__ == "__main__":
    main()
