#!/usr/bin/env bash
# validate-diagrams.sh — Diagram convention + render checker (diagramArchitect skill)
#
# Checks:
#   1. Mermaid sources (*.mmd, *.mermaid) and ```mermaid blocks in Markdown render via mmdc
#   2. PlantUML sources (*.puml, *.plantuml, *.iuml) pass -checkonly
#   3. Every standalone diagram file has the 5-field header
#   4. Mermaid diagrams carry accTitle / accDescr
#   5. Committed images under docs/ with no sibling source (drift risk)   [warning]
#   6. Secret / IP-looking strings in diagram sources                      [warning]
#
# Exit code: non-zero ONLY on real syntax errors or missing headers.
# Missing renderers are reported and skipped, never treated as failures.
#
# Usage: bash scripts/validate-diagrams.sh [root-dir]   (default: current directory)

set -uo pipefail

ROOT="${1:-.}"
ERRORS=0
WARNINGS=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUPPETEER_CFG="$SCRIPT_DIR/../assets/puppeteer-config.json"

PRUNE=(-path '*/node_modules' -o -path '*/.git' -o -path '*/.venv' -o -path '*/venv' -o -path '*/dist' -o -path '*/build' -o -path '*/.data/skills')

find_files() { # $@ = -name patterns joined with -o
  find "$ROOT" \( "${PRUNE[@]}" \) -prune -o -type f \( "$@" \) -print 2>/dev/null
}

MERMAID_FILES="$(find_files -name '*.mmd' -o -name '*.mermaid')"
PUML_FILES="$(find_files -name '*.puml' -o -name '*.plantuml' -o -name '*.iuml')"
MD_WITH_MERMAID="$(find_files -name '*.md' -o -name '*.mdx' | xargs grep -l '^[[:space:]]*```mermaid' 2>/dev/null || true)"

echo "=== Diagram Validator ==="
echo "Root: $ROOT"
echo ""

# ---------- Renderer detection ----------
MMDC=""
if command -v mmdc >/dev/null 2>&1; then
  MMDC="mmdc"
elif command -v npx >/dev/null 2>&1; then
  MMDC="npx -y -p @mermaid-js/mermaid-cli mmdc"
fi

PLANTUML=""
if command -v plantuml >/dev/null 2>&1; then
  PLANTUML="plantuml"
elif [ -n "${PLANTUML_JAR:-}" ] && command -v java >/dev/null 2>&1; then
  PLANTUML="java -jar $PLANTUML_JAR"
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  PLANTUML="docker run --rm -v $(cd "$ROOT" && pwd):/w -w /w plantuml/plantuml"
fi

render_mermaid() { # $1 = input file (.mmd or .md)
  local in="$1" out="$TMP/out-$RANDOM"
  local ext="svg"
  case "$in" in *.md|*.mdx) ext="md" ;; esac
  # mmdc only accepts .md input for markdown; copy .mdx to .md
  local src="$in"
  if [[ "$in" == *.mdx ]]; then src="$TMP/in-$RANDOM.md"; cp "$in" "$src"; fi
  if $MMDC -q -p "$PUPPETEER_CFG" -i "$src" -o "$out.$ext" >"$TMP/log" 2>&1; then
    echo "PASS: $in"
  else
    echo "FAIL: $in"
    sed 's/^/      /' "$TMP/log" | head -15
    ERRORS=$((ERRORS + 1))
  fi
}

# ---------- 1. Mermaid render ----------
echo "--- 1. Mermaid render check ---"
if [ -z "$MERMAID_FILES$MD_WITH_MERMAID" ]; then
  echo "SKIP: no Mermaid sources found"
elif [ -z "$MMDC" ]; then
  echo "SKIP: mmdc/npx not installed — validate manually at https://mermaid.live (non-confidential diagrams only)"
else
  for f in $MERMAID_FILES $MD_WITH_MERMAID; do render_mermaid "$f"; done
fi
echo ""

# ---------- 2. PlantUML syntax ----------
echo "--- 2. PlantUML syntax check ---"
if [ -z "$PUML_FILES" ]; then
  echo "SKIP: no PlantUML sources found"
elif [ -z "$PLANTUML" ]; then
  echo "SKIP: plantuml / java+PLANTUML_JAR / docker not available"
else
  for f in $PUML_FILES; do
    target="$f"
    [[ "$PLANTUML" == docker* ]] && target="${f#"$ROOT"/}"
    if $PLANTUML -checkonly "$target" >"$TMP/log" 2>&1; then
      echo "PASS: $f"
    else
      echo "FAIL: $f"
      sed 's/^/      /' "$TMP/log" | head -15
      ERRORS=$((ERRORS + 1))
    fi
  done
fi
echo ""

# ---------- 3. Header fields (standalone files) ----------
echo "--- 3. Header check (Title, Question, Audience, Source of truth, Last verified) ---"
HEADER_FILES="$MERMAID_FILES $PUML_FILES"
if [ -z "${HEADER_FILES// /}" ]; then
  echo "SKIP: no standalone diagram files"
else
  HDR_ERRORS=0
  for f in $HEADER_FILES; do
    missing=""
    for field in "Title:" "Question:" "Audience:" "Source of truth:" "Last verified:"; do
      head -15 "$f" | grep -q "$field" || missing="$missing ${field%:}"
    done
    if [ -n "$missing" ]; then
      echo "FAIL: $f — missing:$missing"
      HDR_ERRORS=$((HDR_ERRORS + 1))
    fi
  done
  ERRORS=$((ERRORS + HDR_ERRORS))
  [ "$HDR_ERRORS" -eq 0 ] && echo "PASS: all standalone diagrams have headers"
fi
echo ""

# ---------- 4. Accessibility (Mermaid) ----------
echo "--- 4. Accessibility check (accTitle / accDescr) ---"
for f in $MERMAID_FILES; do
  if ! grep -q 'accTitle' "$f" || ! grep -q 'accDescr' "$f"; then
    echo "WARN: $f — missing accTitle/accDescr"
    WARNINGS=$((WARNINGS + 1))
  fi
done
echo ""

# ---------- 5. Images without source ----------
echo "--- 5. Rendered images without source (drift risk) ---"
IMAGES="$(find "$ROOT" \( "${PRUNE[@]}" \) -prune -o -type f \( -path '*docs*' -o -path '*architecture*' -o -path '*adr*' \) \( -name '*.png' -o -name '*.svg' \) -print 2>/dev/null | grep -v '\.drawio\.svg$' || true)"
for img in $IMAGES; do
  base="${img%.*}"
  found=""
  for ext in mmd mermaid puml plantuml drawio excalidraw d2 dsl; do
    [ -f "$base.$ext" ] && found="yes" && break
  done
  if [ -z "$found" ]; then
    echo "WARN: $img — no sibling diagram source"
    WARNINGS=$((WARNINGS + 1))
  fi
done
echo ""

# ---------- 6. Secrets / IPs ----------
echo "--- 6. Confidentiality scan (secrets, IPs) ---"
SCAN="$MERMAID_FILES $PUML_FILES $MD_WITH_MERMAID"
if [ -n "${SCAN// /}" ]; then
  # shellcheck disable=SC2086
  if grep -nEi '(api[_-]?key|secret|passw(or)?d|bearer [a-z0-9]|token=|://[^/ ]+:[^@ ]+@|\b([0-9]{1,3}\.){3}[0-9]{1,3}\b)' $SCAN 2>/dev/null; then
    echo "WARN: review the lines above — no secrets, credentials, or internal IPs in diagrams"
    WARNINGS=$((WARNINGS + 1))
  else
    echo "PASS: no secret/IP patterns"
  fi
fi
echo ""

echo "=== Result: $ERRORS error(s), $WARNINGS warning(s) ==="
[ "$ERRORS" -eq 0 ]
