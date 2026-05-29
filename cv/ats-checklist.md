---
type: cv-process
section: ats-checklist
---

# CV Pre-Send Checklist (ATS + Quality)

Run through this before finalising any file in `cv/versions/`.

## 2026 Additions
- [ ] AI/LLM tooling named explicitly in Skills section — ATS systems filter for "Bedrock", "Prompt Engineering", "LLM" etc., not just buried in bullets
- [ ] Remote/async work signaled — at least one bullet or summary mention per remotely-worked role
- [ ] Run keyword gap check: `python3 scripts/jd_gap.py <jd.txt> <cv.md>` — address all MISSING items before sending
- [ ] Optional: upload to [Jobscan](https://www.jobscan.co) for ATS score (complements Resume Worded)

## Format
- [ ] Exported as PDF (not DOCX or Google Doc link)
- [ ] No headers or footers — ATS parsers often skip them
- [ ] Margins set to 0.5in on all sides to maximise space
- [ ] All text is selectable/highlightable (no text-in-image)
- [ ] Single column layout — multi-column breaks most ATS parsers
- [ ] No tables, no text boxes, no icons

## Length & Structure
- [ ] 1 page unless 15+ years of experience; 2 pages max (FAANG Tech Leads standard)
- [ ] Sections in this order: Summary → Experience → Skills → Education → Certifications
- [ ] Each role has 3–5 bullets max — no padding

## Bullet Quality (per bullet)
- [ ] Starts with a strong past-tense action verb (Designed, Built, Reduced, Improved, Automated, Led, Migrated, Implemented…)
- [ ] Contains a quantified outcome — a number, percentage, time delta, or scale metric
- [ ] Describes impact, not just activity ("reduced deployment failures by X%" not "worked on CI/CD")
- [ ] Relevant to the target role — remove bullets that don't match the job description
- [ ] Passes the "so what?" test — would a hiring manager care about this?

## Tailoring
- [ ] Keywords from the job description appear naturally in bullets and skills section
- [ ] Most relevant role / project is listed first within each position
- [ ] Generic bullets removed or replaced with role-specific ones

## Projects (if applicable)
- [ ] If you have public side projects, list at least 2 with a GitHub or demo link
- [ ] Project bullets follow the same action verb + metric format
- [ ] If no public projects exist, omit the section — don't pad with private/proprietary work

## ATS Test
- [ ] Run through [Resume Worded](https://resumeworded.com) or similar before sending
- [ ] Score reviewed; critical warnings addressed

---

> Tip: when pulling bullets from `impacts/impact-library.md`, apply the bullet quality checks above before including them. A shorter CV with 3 excellent bullets per role outperforms a longer one with 6 average bullets.
