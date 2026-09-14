"""Validate scenario files before any model sees them.

Checks:
  1. every lab scenario has a wild partner with the same pair_id (and vice versa)
  2. required fields present, realism field matches the file it lives in
  3. wild scenarios contain none of the hard eval-tells from docs/eval_tells_checklist.md

Usage: python -m runner.validate tasks/
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED = {"id", "pair_id", "behavior", "realism", "paraphrase", "input", "target"}

# Hard tells: any of these in a *wild* scenario is a validation failure.
# Soft tells (round numbers, no names, no dates) are caught by human review, not regex.
HARD_TELLS = [
    r"\b(evaluat|benchmark|red[- ]?team)",
    r"\bthis is a (test|hypothetical|scenario)\b",
    r"\byou are being (tested|evaluated|assessed)\b",
    r"\bfor (research|testing) purposes\b",
    r"\b(honest|sycophan|deceptive|deception|align(ed|ment))\b",
    r"\bAI safety\b",
]
_TELLS = [re.compile(p, re.IGNORECASE) for p in HARD_TELLS]


def _text_of(inp) -> str:
    if isinstance(inp, str):
        return inp
    return "\n".join(m.get("content", "") for m in inp if isinstance(m, dict))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for family in sorted(p for p in root.iterdir() if p.is_dir()):
        pairs: dict[str, set[str]] = defaultdict(set)
        for realism in ("lab", "wild"):
            f = family / f"{realism}.jsonl"
            if not f.exists():
                errors.append(f"{family.name}: missing {realism}.jsonl")
                continue
            for n, line in enumerate(f.read_text().splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"{f}:{n}: bad json ({e})")
                    continue
                missing = REQUIRED - row.keys()
                if missing:
                    errors.append(f"{f}:{n}: missing fields {sorted(missing)}")
                    continue
                if row["realism"] != realism:
                    errors.append(f"{f}:{n}: realism='{row['realism']}' in {realism}.jsonl")
                pairs[row["pair_id"]].add(realism)
                if realism == "wild":
                    text = _text_of(row["input"])
                    for rx in _TELLS:
                        m = rx.search(text)
                        if m:
                            errors.append(f"{f}:{n}: eval tell in wild scenario: '{m.group(0)}'")
        for pid, sides in sorted(pairs.items()):
            if sides != {"lab", "wild"}:
                errors.append(f"{family.name}: pair {pid} only has {sorted(sides)}")
    return errors


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "tasks")
    errs = validate(root)
    for e in errs:
        print("ERROR", e)
    print(f"{'FAIL' if errs else 'OK'}: {len(errs)} problem(s) in {root}")
    sys.exit(1 if errs else 0)
