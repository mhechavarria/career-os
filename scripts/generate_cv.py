#!/usr/bin/env python3
"""
generate_cv.py — ATS-compliant PDF generator for Career OS CV files.

Usage:
    python3 scripts/generate_cv.py cv/versions/acme-staff-backend.md
    python3 scripts/generate_cv.py cv/master.md --output ~/Desktop/cv.pdf
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Preprocessing — strip Obsidian-specific syntax
# ---------------------------------------------------------------------------


def preprocess(text: str) -> str:
    # Remove YAML frontmatter block
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)

    # Remove dataview code blocks entirely
    text = re.sub(r"```dataview.*?```", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove other fenced code blocks (leave content, remove fences)
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text, flags=re.DOTALL)

    # Strip Obsidian wiki links — keep display text: [[file|label]] → label, [[file]] → file
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # Strip inline Dataview metadata tags: [field:: value]
    text = re.sub(r"\[[^\[\]]+::[^\[\]]+\]", "", text)

    # Strip blockquotes — used as editorial notes in tailored CVs, not output content
    text = re.sub(r"(^|\n)(>[^\n]*\n?)+", "\n", text)

    # Collapse lines that became empty after stripping
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# ATS validation — print warnings, never block PDF generation
# ---------------------------------------------------------------------------


def validate_ats(text: str, source: str) -> None:
    warnings = []

    # Format checks
    if re.search(r"^\|[-| :]+\|", text, re.MULTILINE):
        warnings.append(
            "Tables detected — ATS parsers cannot read markdown tables. Convert to plain lists."
        )

    if re.search(r"!\[", text):
        warnings.append(
            "Images found — ATS systems ignore images. Remove or replace with text."
        )

    if re.search(r"\[\[", text):
        warnings.append(
            "Obsidian wiki links still present — check preprocessing output."
        )

    if re.search(r"\[[^\[\]]+::", text):
        warnings.append(
            "Dataview inline tags still present — check preprocessing output."
        )

    # Contact completeness
    if not re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text):
        warnings.append(
            "No email address found — email is required in the contact block."
        )

    if not re.search(r"\+?\d[\d\s\-\(\)\.]{7,}\d", text):
        warnings.append(
            "No phone number found — phone is required in the contact block."
        )

    # Date format — only check inside the Experience block, not Education
    experience_for_dates = re.search(
        r"\n## Experience\n(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE
    )
    if experience_for_dates and re.search(
        r"\b(19|20)\d{2}\s*[–\-]\s*(19|20)\d{2}\b", experience_for_dates.group(1)
    ):
        warnings.append(
            "Year-only date ranges found in Experience (e.g. 2021–2023) — use MMM YYYY format (e.g. Jul 2021 – Dec 2023)."
        )

    # First-person pronouns in bullet content
    if re.search(
        r"^[-*]\s[^\n]*\b(I|me|we|our|my)\b", text, re.MULTILINE | re.IGNORECASE
    ):
        warnings.append(
            "First-person pronouns (I/me/we/our/my) found in bullets — start bullets with action verbs instead."
        )

    # Experience block checks (bullets per role + unquantified bullets)
    experience_block = re.search(
        r"\n## Experience\n(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE
    )
    if experience_block:
        exp_text = experience_block.group(1)

        # Bullet count per role
        role_sections = re.split(r"\n### ", exp_text)
        for section in role_sections:
            bullets = re.findall(r"^[-*] ", section, re.MULTILINE)
            if len(bullets) > 5:
                header = section.split("\n")[0].strip()
                warnings.append(
                    f"Role '{header[:60]}' has {len(bullets)} bullets — keep max 5 per role."
                )

        # Bullets without any quantified metric
        all_bullets = re.findall(r"^[-*] (.+)$", exp_text, re.MULTILINE)
        unquantified = [b[:70] for b in all_bullets if not re.search(r"\d", b)]
        if unquantified:
            sample = "\n".join(f"    → {b}…" for b in unquantified[:3])
            warnings.append(
                f"{len(unquantified)} bullet(s) with no number/metric (XYZ formula: add %, count, time, $):\n{sample}"
            )

    if warnings:
        print(f"\n[ATS WARNINGS] {source}", file=sys.stderr)
        for w in warnings:
            print(f"  ⚠  {w}", file=sys.stderr)
        print("", file=sys.stderr)


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

CSS_PATH = Path(__file__).parent / "cv_style.css"


def to_html(markdown_text: str) -> str:
    import markdown2

    body = markdown2.markdown(
        markdown_text,
        extras=["strike", "header-ids"],
    )

    css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------


def to_pdf(html: str, output_path: Path) -> int:
    """Render the HTML to a PDF file and return the rendered page count."""
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration

    font_config = FontConfiguration()
    document = HTML(string=html).render(
        font_config=font_config,
        presentational_hints=True,
    )
    document.write_pdf(str(output_path))
    return len(document.pages)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an ATS-compliant PDF from a Career OS CV markdown file."
    )
    parser.add_argument("input", help="Path to the CV markdown file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output PDF path (default: same location as input, .pdf extension)",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = (
        Path(args.output).resolve() if args.output else input_path.with_suffix(".pdf")
    )

    print(f"Reading  {input_path}")

    raw = input_path.read_text(encoding="utf-8")
    clean = preprocess(raw)
    validate_ats(clean, input_path.name)

    html = to_html(clean)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Rendering PDF...")
    pages = to_pdf(html, output_path)
    if pages > 2:
        print(
            f"\n[ATS WARNINGS] {input_path.name}\n"
            f"  ⚠  CV rendered to {pages} pages — the 2-page cap is exceeded. "
            f"Trim bullets or tighten content.\n",
            file=sys.stderr,
        )

    print(f"Done →   {output_path} ({pages} page{'s' if pages != 1 else ''})")


if __name__ == "__main__":
    main()
