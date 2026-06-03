# sources/ — raw intake material

Drop existing career material here to **seed** your Career OS intake: an old CV, your
LinkedIn profile text, a past performance review. During **Phase 0** of
[`../AGENT.md`](../AGENT.md), the AI agent reads whatever is in this folder and
pre-fills the factual scaffolding — names, titles, dates, skills — so the interview
can focus on what those documents almost never contain: quantified outcomes,
evidence, and stories.

## What to drop here

- **Old CV** — `.md`, `.txt`, or `.pdf`. Markdown and text are read directly; a PDF is
  read directly by agents that support it (Claude Code does). For `.docx`, export to
  PDF or paste the text.
- **LinkedIn** — paste your *About* section and experience into a `.txt`, or drop your
  official data export (*Settings → Get a copy of your data*). Don't rely on scraping
  a live profile URL.
- **Anything else with evidence** — past performance reviews, brag notes, project
  writeups.

## Seed, not source of truth

The agent treats everything here as **claims to verify**, not finished content. Old
CVs are full of vague, unquantified bullets and LinkedIn "About" sections are
marketing prose — Career OS trades in evidence, not adjectives. Imported bullets
without a number come back as `- [ ] TODO:` items for you to quantify in the
interview, and nothing here is copied into your CV unedited.

## Privacy

Raw material here carries PII — phone, address, full history. By default this folder
is **gitignored** (everything except this README), so your old CV never lands in
version control. If this is your own private instance and you *want* that history
tracked, remove the `sources/` rule from [`../.gitignore`](../.gitignore).
