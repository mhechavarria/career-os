# Security Policy

Career OS is a template repository. It has no hosted runtime, no server, and
collects no data — the scripts run locally and only read/write files in your
own clone.

## Reporting an issue

If you find a security-relevant problem in the tooling (for example, a script
that could execute untrusted input or leak file contents), please open a
[GitHub issue](../../issues) describing it. There is no private runtime to
exploit, so public disclosure is acceptable.

## Protecting your own data

This repo ships **blank skeletons only**. Once you fill it with your real
career history, treat your clone as personal data:

- Keep your filled-in fork **private** if it contains contact details or
  unpublished work history.
- Generated PDFs are git-ignored by default (`*.pdf`) — do not force-add them.
- Never commit credentials, API keys, or `.env` files.
