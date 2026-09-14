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


def _valid_input(inp) -> bool:
    if isinstance(inp, str):
        return bool(inp.strip())
    if not isinstance(inp, list) or not inp:
        return False
    return all(
        isinstance(message, dict)
        and message.get("role") in {"system", "user", "assistant"}
        and isinstance(message.get("content"), str)
        and bool(message["content"].strip())
        for message in inp
    )


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for family in sorted(p for p in root.iterdir() if p.is_dir()):
        pairs: dict[str, set[str]] = defaultdict(set)
        pair_rows: dict[str, dict[str, list[tuple[int, dict, int]]]] = defaultdict(
            lambda: defaultdict(list)
        )
        seen_ids: dict[str, Path] = {}
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
                if not isinstance(row, dict):
                    errors.append(f"{f}:{n}: row must be a JSON object")
                    continue
                missing = REQUIRED - row.keys()
                if missing:
                    errors.append(f"{f}:{n}: missing fields {sorted(missing)}")
                    continue
                if row["realism"] != realism:
                    errors.append(f"{f}:{n}: realism='{row['realism']}' in {realism}.jsonl")
                for field in ("id", "pair_id", "behavior"):
                    if not isinstance(row[field], str) or not row[field].strip():
                        errors.append(f"{f}:{n}: {field} must be a non-empty string")
                if (isinstance(row["paraphrase"], bool)
                        or not isinstance(row["paraphrase"], int)
                        or row["paraphrase"] < 0):
                    errors.append(f"{f}:{n}: paraphrase must be a non-negative integer")
                if not _valid_input(row["input"]):
                    errors.append(f"{f}:{n}: input must be a non-empty string or message list")
                if not isinstance(row["target"], str) or not row["target"].strip():
                    errors.append(f"{f}:{n}: target must be a non-empty string")
                if isinstance(row["id"], str):
                    if row["id"] in seen_ids:
                        errors.append(f"{f}:{n}: duplicate id '{row['id']}' (already in {seen_ids[row['id']]})")
                    else:
                        seen_ids[row["id"]] = f
                valid_pair_id = isinstance(row["pair_id"], str) and bool(row["pair_id"].strip())
                valid_paraphrase = isinstance(row["paraphrase"], int) and not isinstance(
                    row["paraphrase"], bool
                ) and row["paraphrase"] >= 0
                if valid_pair_id:
                    pairs[row["pair_id"]].add(realism)
                    if valid_paraphrase:
                        pair_rows[row["pair_id"]][realism].append((row["paraphrase"], row, n))
                if realism == "wild":
                    text = _text_of(row["input"])
                    for rx in _TELLS:
                        m = rx.search(text)
                        if m:
                            errors.append(f"{f}:{n}: eval tell in wild scenario: '{m.group(0)}'")
        for pid, sides in sorted(pairs.items()):
            if sides != {"lab", "wild"}:
                errors.append(f"{family.name}: pair {pid} only has {sorted(sides)}")
                continue
            side_rows = pair_rows[pid]
            side_sets = {
                side: [row[0] for row in side_rows[side]] for side in ("lab", "wild")
            }
            for side in side_rows:
                paraphrases = side_sets[side]
                if len(paraphrases) != len(set(paraphrases)):
                    errors.append(f"{family.name}: pair {pid} has duplicate {side} paraphrase")
            if set(side_sets["lab"]) != set(side_sets["wild"]):
                errors.append(
                    f"{family.name}: pair {pid} has mismatched paraphrases "
                    f"(lab={sorted(set(side_sets['lab']))}, wild={sorted(set(side_sets['wild']))})"
                )
            behaviors = {
                side: {row[1]["behavior"] for row in side_rows[side]} for side in ("lab", "wild")
            }
            if behaviors["lab"] != behaviors["wild"]:
                errors.append(f"{family.name}: pair {pid} has mismatched behavior metadata")
    return errors


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "tasks")
    errs = validate(root)
    for e in errs:
        print("ERROR", e)
    print(f"{'FAIL' if errs else 'OK'}: {len(errs)} problem(s) in {root}")
    sys.exit(1 if errs else 0)
