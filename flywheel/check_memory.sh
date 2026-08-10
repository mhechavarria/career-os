#!/usr/bin/env bash
# check_memory.sh — read-only integrity check for a Judgment Flywheel memory store.
#
# Read-only: writes nothing, so it is safe to run from a git hook.
#
# Exit 0 = clean (warnings allowed). Exit 1 = at least one FAIL.
#
# Deliberately uses grep/awk only, not `rg`: `rg` may be a shell function or
# simply absent inside a git hook's minimal environment, so it cannot be
# relied on there.

set -uo pipefail
MEMDIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
FAIL=0
WARN=0
# Findings accumulate newline-separated, never space-separated: a memory
# filename may legitimately contain spaces, and joining on spaces would split
# one real name into several bogus ones in the report the operator acts on.
NL=$'\n'

fail() { echo "  FAIL  $*"; FAIL=$((FAIL + 1)); }
warn() { echo "  warn  $*"; WARN=$((WARN + 1)); }

# Files that live here but are not memories. Extend this list locally if your
# store keeps other meta files alongside the memories.
is_meta() {
  case "$1" in
    MEMORY.md | ARCHIVE.md | README.md) return 0 ;;
    *) return 1 ;;
  esac
}

echo "memory check: $MEMDIR"

[ -f "$MEMDIR/MEMORY.md" ] || {
  echo "  FAIL  MEMORY.md missing — the index IS the memory system"
  exit 1
}

# 1. Index budget. These bands measure the auto-loaded context budget, not the
#    store's total size — the same numbers apply to every session, and are
#    meant to be edited locally if your harness's context budget differs.
#    Red is a hard stop; amber only warns.
BYTES=$(wc -c < "$MEMDIR/MEMORY.md")
if [ "$BYTES" -ge 20000 ]; then
  fail "index $BYTES bytes [RED] — sweep to under 12,000 before pushing"
elif [ "$BYTES" -ge 16000 ]; then
  warn "index $BYTES bytes [AMBER] — an archive sweep is due"
else
  echo "  ok    index $BYTES bytes [GREEN]"
fi

# 2. Index-line cap. A hook is a hook, not a changelog. Same selector as the
#    save-memory skill's own manual verifier, so the two checks cannot disagree.
OVER=$(grep '^- \[' "$MEMDIR/MEMORY.md" | awk '{ if (length($0) > 160) print length($0)": "substr($0,1,50) }')
if [ -n "$OVER" ]; then
  fail "index line(s) over the 160-char cap:"
  while IFS= read -r line; do echo "          $line"; done <<< "$OVER"
fi

# 3. Every body resolves to an index line. A body no index line points at is
#    invisible to a returning session.
MISSING=""
BODIES=0
for f in "$MEMDIR"/*.md "$MEMDIR"/archive/*.md; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  is_meta "$base" && continue
  BODIES=$((BODIES + 1))
  rel="$base"
  case "$f" in
    */archive/*) rel="archive/$base" ;;
  esac
  if ! grep -q "](\(archive/\)\?$base)" "$MEMDIR/MEMORY.md" 2> /dev/null &&
    ! { [ -f "$MEMDIR/ARCHIVE.md" ] && grep -q "](\(archive/\)\?$base)" "$MEMDIR/ARCHIVE.md" 2> /dev/null; }; then
    MISSING="$MISSING$rel$NL"
  fi
done
if [ -n "$MISSING" ]; then
  fail "body file(s) with no index line — a returning session would see only a bare filename:"
  while IFS= read -r m; do [ -n "$m" ] && echo "          $m"; done <<< "$MISSING"
else
  echo "  ok    all $BODIES bodies resolve to an index line"
fi

# 4. Every index link points at a file that exists AND is tracked by git.
#
#    "Exists on disk" alone is not enough for a pre-push gate. An index line can
#    be committed while its body stays untracked — that pushes a dangling link
#    which is invisible on this machine and only breaks for whoever clones,
#    which is exactly the handoff case. Reported as a separate failure because
#    the fix is different: a missing file needs writing, an untracked one needs
#    `git add`.
#
#    Residual gap, accepted deliberately: a body that is staged but not yet
#    committed passes here while still being absent from the pushed tree.
#    Checking HEAD instead would close it, but would also fire during ordinary
#    edit cycles when this script is run standalone, and a noisy gate gets
#    bypassed.
#    The question here is "is MEMDIR its own repo root?", not "is MEMDIR inside
#    some repo?". `rev-parse --git-dir` answers the second one, so a memory
#    directory merely nested under an unrelated ancestor repo — a dotfiles repo
#    rooted at $HOME is the common case — would be checked against that
#    ancestor's index and report every body as untracked. Compare against
#    `--show-toplevel` instead. This mirrors the same check in
#    skills/save-memory/SKILL.md; the manual and automated gates must not disagree.
#
#    Both sides are canonicalized before comparing. MEMDIR arrives verbatim from
#    $1, so it may be relative, carry a trailing slash, or contain `..`, while
#    --show-toplevel always prints an absolute path with none of those. A literal
#    string comparison would then miss a genuine repo root and silently skip the
#    tracking check — a worse failure than the one above, because it is silent.
GITREPO=0
MEMDIR_REAL=$(cd "$MEMDIR" 2> /dev/null && pwd -P)
TOPLEVEL=$(git -C "$MEMDIR" rev-parse --show-toplevel 2> /dev/null)
if [ -n "$TOPLEVEL" ] && [ -n "$MEMDIR_REAL" ]; then
  TOPLEVEL_REAL=$(cd "$TOPLEVEL" 2> /dev/null && pwd -P)
  [ "$MEMDIR_REAL" = "$TOPLEVEL_REAL" ] && GITREPO=1
fi

DANGLING=""
UNTRACKED=""
while IFS= read -r target; do
  [ -n "$target" ] || continue
  if [ ! -f "$MEMDIR/$target" ]; then
    DANGLING="$DANGLING$target$NL"
  elif [ "$GITREPO" -eq 1 ] && ! git -C "$MEMDIR" ls-files --error-unmatch "$target" > /dev/null 2>&1; then
    UNTRACKED="$UNTRACKED$target$NL"
  fi
  # The link-target class is "anything but a slash or a closing paren", not a
  # narrow ASCII set. A narrow set silently DROPS links whose filename holds a
  # space or an accented letter, so a genuinely missing or untracked body of
  # that name is reported as ok — the exact failure this check exists to catch.
  # `/` stays excluded so a crafted index cannot walk out of the memory
  # directory; the optional archive/ prefix is matched explicitly instead.
done < <(grep -oh '](\(archive/\)\?[^)/]*\.md)' "$MEMDIR/MEMORY.md" "$MEMDIR/ARCHIVE.md" 2> /dev/null | sed 's/^](//; s/)$//')

if [ -n "$DANGLING" ]; then
  fail "index link(s) pointing at a missing file:"
  while IFS= read -r d; do [ -n "$d" ] && echo "          $d"; done <<< "$DANGLING"
fi
if [ -n "$UNTRACKED" ]; then
  fail "index link(s) whose body is NOT tracked by git — a clone would see a dangling link:"
  while IFS= read -r u; do [ -n "$u" ] && echo "          $u  (git add \"$u\")"; done <<< "$UNTRACKED"
fi
if [ -z "$DANGLING" ] && [ -z "$UNTRACKED" ]; then
  if [ "$GITREPO" -eq 1 ]; then
    echo "  ok    every index link resolves to a tracked file"
  else
    echo "  ok    every index link resolves to a file on disk (not a git repo — tracking unchecked)"
  fi
fi

# 5. Frontmatter matching the documented file format (name / type / description).
BADFM=""
for f in "$MEMDIR"/*.md "$MEMDIR"/archive/*.md; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  is_meta "$base" && continue
  slug=$(awk -F': *' '/^name:/{print $2; exit}' "$f" | tr -d '"' | tr '[:upper:] ' '[:lower:]-')
  mtype=$(awk '/^  type:|^type:/{print $2; exit}' "$f" | tr -d '"')
  desc=$(awk -F'description: *' '/^description:/{print $2; exit}' "$f")
  [ -z "$slug" ] && BADFM="$BADFM$base (name)$NL"
  [ -z "$mtype" ] && BADFM="$BADFM$base (type)$NL"
  [ -z "$desc" ] && BADFM="$BADFM$base (description)$NL"
done
if [ -n "$BADFM" ]; then
  fail "frontmatter that does not match the documented file format — cannot parse:"
  while IFS= read -r b; do [ -n "$b" ] && echo "          $b"; done <<< "$BADFM"
else
  echo "  ok    frontmatter readable in all $BODIES bodies"
fi

echo
if [ "$FAIL" -gt 0 ]; then
  echo "MEMORY CHECK FAILED — $FAIL problem(s), $WARN warning(s)"
  echo "Fix, or push anyway with:  git push --no-verify"
  exit 1
fi
echo "memory check passed — $WARN warning(s)"
exit 0
