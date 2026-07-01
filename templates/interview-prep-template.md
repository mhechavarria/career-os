---
type: company
company: <% await tp.system.prompt("Company name") %>
doc: interview-prep
status: <% await tp.system.prompt("Status (researching/applied/interviewing/offer/closed)", "interviewing") %>
tags: []
---

# <% await tp.system.prompt("Company name") %> — Interview Prep

> Turn research into a plan for the room. See [[research]] for company intel and
> [[people]] for who is across the table. The single highest-value move: read
> [[people]] first — if you know the interviewer's background, reorder which STAR story
> you lead with to match it (an SRE interviewer → lead with the reliability story).

## Process

> What are the actual stages, and which one is the real bar? Pull from the recruiter,
> the careers page, and public reports (treat Glassdoor as directional, and say so).
> _Example: "Recruiter screen → technical call → a paid work-day with the team. The
> work-day is the bar — be ready to ship in their stack and reason out loud."_

-

## Recruiter / First Call

> The screen is logistics and fit, not depth — but it sets your level and your comp
> anchor. Confirm the basics and get the band before you invest in deep prep.
> _Example: "Confirm: level this maps to, comp band, remote/timezone, process length,
> visa/eligibility. Have a one-line 'why this company' and your salary range ready."_

- **Level this maps to:**
- **Comp band (ask early):**
- **Logistics (timezone / format / eligibility):**
- **My one-line pitch for this role:**

## Likely Themes

> What will they probe, derived from the JD's "what you'll do"? List the 4–6 themes so
> every one has a story mapped to it below.
> _Example: "Event-driven design at scale; reliability/idempotency; high ownership."_

-

## STAR Stories to Lead With

> Map your already-documented stories (`impacts/`, `experience/`) to the themes above —
> one vivid specific per theme, name the mechanism, land a company-tied punchline. Do
> not invent stories; select and sharpen the real ones. Reuse
> [[star-stories-template]] for full detail.
> _Example: "Theme: reliability → the webhook fan-out I moved to a worker fleet with a
> DLQ and idempotency keys, taking callback failures from weekly to near-zero."_

- **Theme →** story → the one detail:

## System-Design Prep

> Senior/staff only: prep the one design question their product most likely implies,
> and map it onto their actual stack (from [[research]]) so you design in their world.
> _Example: "Design their core sync/ingestion engine — cover cursors, idempotency,
> backpressure, per-tenant isolation — on Postgres + Redis + their queue."_

-

## Take-Home / Work-Trial Prep

> If the process has a take-home or paid work-day, that is usually the real bar. Note
> the format, timebox, and how you'll show judgment (tests, a short README, trade-offs).
> _Example: "Timebox 3h; ship a small but tested slice; write a README on what you cut
> and why. Don't gold-plate."_

-

## Questions to Ask Them

> Questions that signal you understood their specific situation, not generic ones.
> Pull the sharp ones from `research.md`'s Open Questions.
> _Example: "What drove the move off <tool> to a custom one — and what did you trade?"_

- [ ]

## Prep Checklist

> The concrete to-dos before the call — including confirming the logistics.

- [ ] Confirm date, timezone, and format
- [ ] Re-read the JD; map each "what you'll do" bullet to one story above
- [ ] Rehearse the system-design question out loud (senior/staff)
- [ ] Read [[people]]; reorder STAR leads to the known interviewer
- [ ] Prepare the honest answer to this role's weakest gap
