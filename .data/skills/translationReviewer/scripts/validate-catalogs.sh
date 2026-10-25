#!/usr/bin/env bash
# One-shot mechanical pass for a translation PR. Run from the repo root.
#   validate-catalogs.sh <base-ref> <head-ref> [keep-term ...]
#   validate-catalogs.sh origin/master pr-3791 brandix "FlowKit X"
# 1. project checker (if the repo has one)  2. check_catalogs.py  3. msgfmt -c on changed .po files
set -uo pipefail
BASE=${1:?base ref}; HEAD=${2:?head ref}; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEEP=(); for t in "$@"; do KEEP+=(--keep "$t"); done
status=0

# project PR checker (tracked or untracked), e.g. server/scripts/check_translation_pr.py
proj=$({ git ls-files; git ls-files --others --exclude-standard; } | grep -E '(^|/)check_translations?_pr[^/]*\.py$' | grep -v '/tests\?/' | head -1)
if [[ -n "$proj" ]]; then
  echo "##### project checker: $proj"
  pr="${HEAD#pr-}"
  if [[ "$pr" =~ ^[0-9]+$ ]]; then python3 "$proj" "$pr" || status=1; else python3 "$proj" "$HEAD" --base "$BASE" || status=1; fi
fi

echo; echo "##### check_catalogs.py"
python3 "$HERE/check_catalogs.py" --base "$BASE" --head "$HEAD" "${KEEP[@]}" || status=1

if command -v msgfmt >/dev/null; then
  echo; echo "##### msgfmt -c (changed .po files)"
  tmp=$(mktemp -d); bad=0
  while IFS= read -r f; do
    [[ "$f" == *.po ]] || continue
    git show "$HEAD:$f" > "$tmp/x.po" 2>/dev/null || continue
    out=$(msgfmt -c -o /dev/null "$tmp/x.po" 2>&1 | grep -v -E 'PO-Revision-Date|Project-Id-Version|header field|Language-Team|Last-Translator|Charset')
    [[ -n "$out" ]] && { echo "$f"; echo "$out" | head -5; bad=1; }
  done < <(git diff --name-only "$(git merge-base "$BASE" "$HEAD")" "$HEAD")
  rm -rf "$tmp"; [[ $bad == 0 ]] && echo "clean" || status=1
fi
exit $status
