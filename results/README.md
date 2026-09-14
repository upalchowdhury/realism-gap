# Results directory

Reviewed aggregate exports belong here when a pilot is complete. The default
`.gitignore` keeps `results/*.csv` local because raw and provisional results should be
reviewed before publication.

The dashboard expects `gap_table.csv` with one row per model/behavior and these
columns:

`model`, `behavior`, `gap`, `ci_lo`, `ci_hi`, `n_pairs`

Build the page with:

```bash
python -m analysis.dashboard results/gap_table.csv dashboard/index.html
```

Do not hand-edit aggregate values. Generate them from validated exports using the
analysis code, retain the source manifest and score files, and record the producing
commit before making a result public.
