"""Render a dependency-light static dashboard from an aggregated gap table."""

import html
import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"model", "behavior", "gap", "ci_lo", "ci_hi", "n_pairs"}


def render_dashboard(table: pd.DataFrame | None = None) -> str:
    """Return a self-contained HTML dashboard for a gap table.

    The empty state is intentional: it explains that no benchmark result exists
    rather than displaying placeholder numbers. ``table`` is expected to contain
    one aggregated row per model/behavior, as emitted by ``analysis.gap``.
    """

    if table is None:
        table = pd.DataFrame()
    if not table.empty:
        missing = sorted(REQUIRED_COLUMNS - set(table.columns))
        if missing:
            raise ValueError(f"dashboard table missing columns: {missing}")
        table = table.sort_values(["behavior", "gap"], ascending=[True, False])

    rows = []
    max_gap = (
        max((abs(float(value)) for value in table["gap"]), default=0.1)
        if not table.empty
        else 0.1
    )
    max_gap = max(max_gap, 0.1)
    for record in table.to_dict("records"):
        gap = float(record["gap"])
        width = min(abs(gap) / max_gap * 45, 45)
        left = 50 if gap >= 0 else 50 - width
        direction = "wild higher" if gap >= 0 else "wild lower"
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(record['model']))}</td>"
            f"<td>{html.escape(str(record['behavior']))}</td>"
            f"<td><strong>{gap:+.3f}</strong><div class=\"bar-track\" aria-label=\"{gap:+.3f}, {direction}\">"
            f"<span class=\"zero\"></span><span class=\"bar {'positive' if gap >= 0 else 'negative'}\" style=\"left:{left:.2f}%;width:{width:.2f}%\"></span></div></td>"
            f"<td>[{float(record['ci_lo']):+.3f}, {float(record['ci_hi']):+.3f}]</td>"
            f"<td>{int(record['n_pairs'])}</td>"
            "</tr>"
        )

    if rows:
        content = (
            f"<p class=\"lede\">{len(table)} model/behavior estimates from "
            f"{int(table['n_pairs'].sum())} pair observations counted across rows.</p>"
            "<div class=\"legend\"><span class=\"swatch positive\"></span> wild higher than lab "
            "<span class=\"swatch negative\"></span> wild lower than lab</div>"
            "<div class=\"table-wrap\"><table><thead><tr>"
            "<th>Model</th><th>Behavior</th><th>Gap (wild − lab)</th><th>95% CI</th><th>Pairs</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )
    else:
        content = (
            "<div class=\"empty\"><div class=\"empty-mark\">∅</div>"
            "<h2>No published results yet</h2>"
            "<p>This page is ready for reviewed exports. The repository currently contains "
            "plumbing fixtures and no benchmark measurements.</p></div>"
        )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>realism-gap · results</title>
<style>
:root {{ color-scheme: light; --ink:#17202a; --muted:#607080; --line:#d8e0e8;
  --paper:#f7f9fb; --card:#fff; --positive:#197b62; --negative:#b34b4b; --accent:#315c9b; }}
* {{ box-sizing:border-box }} body {{ margin:0; background:var(--paper); color:var(--ink);
  font:15px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
main {{ max-width:1100px; margin:0 auto; padding:56px 24px 72px; }}
header {{ border-bottom:1px solid var(--line); margin-bottom:28px; padding-bottom:24px; }}
h1 {{ font-size:clamp(2rem,5vw,3.4rem); letter-spacing:-.04em; margin:0 0 6px; }}
h2 {{ margin:0 0 8px; }} .kicker {{ color:var(--accent); font-weight:700; letter-spacing:.08em;
  text-transform:uppercase; font-size:.76rem; }} .lede {{ color:var(--muted); margin-top:0; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:22px;
  box-shadow:0 5px 18px rgba(25,50,75,.05); }} .empty {{ text-align:center; padding:70px 20px; }}
.empty-mark {{ align-items:center; background:#edf2f7; border-radius:50%; color:var(--accent);
  display:flex; font-size:2rem; height:64px; justify-content:center; margin:0 auto 16px; width:64px; }}
.empty p {{ color:var(--muted); margin:0 auto; max-width:560px; }} .legend {{ color:var(--muted); font-size:.85rem;
  margin:0 0 14px; }} .swatch {{ border-radius:3px; display:inline-block; height:10px; margin:0 5px 0 14px; width:18px; }}
.swatch:first-child {{ margin-left:0; }} .positive {{ background:var(--positive); }} .negative {{ background:var(--negative); }}
.table-wrap {{ overflow-x:auto; }} table {{ border-collapse:collapse; min-width:760px; width:100%; }}
th {{ color:var(--muted); font-size:.78rem; letter-spacing:.04em; text-align:left; text-transform:uppercase; }}
th,td {{ border-bottom:1px solid var(--line); padding:13px 10px; vertical-align:middle; }}
tr:last-child td {{ border-bottom:0; }} td:nth-child(3) {{ min-width:260px; }} .bar-track {{ background:#edf1f5;
  border-radius:5px; height:10px; margin-top:7px; overflow:hidden; position:relative; }} .zero {{ background:#718096;
  height:100%; left:50%; position:absolute; width:1px; z-index:2; }} .bar {{ border-radius:5px; height:100%; position:absolute; }}
footer {{ color:var(--muted); font-size:.82rem; margin-top:22px; }} code {{ background:#edf2f7; border-radius:4px; padding:2px 5px; }}
@media (max-width:600px) {{ main {{ padding:32px 14px 52px; }} .card {{ padding:14px; }} }}
</style></head><body><main>
<header><div class="kicker">Paired realism evaluation</div><h1>realism-gap</h1>
<p class="lede">Does the same model behave differently when a task looks like a test?</p></header>
<section class="card">{content}</section>
<footer>Gap = P(misbehave | wild) − P(misbehave | lab). Bars show direction and relative magnitude;
 intervals are paired-bootstrap 95% CIs. See the repository README for methods and limitations.</footer>
</main></body></html>
"""


def write_dashboard(input_path: Path, output_path: Path) -> None:
    table = pd.read_csv(input_path) if input_path.exists() else None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dashboard(table))


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/gap_table.csv")
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("dashboard/index.html")
    write_dashboard(source, destination)
    print(f"Wrote {destination} ({'results' if source.exists() else 'empty state'})")
