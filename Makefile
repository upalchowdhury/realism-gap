.PHONY: validate test lint smoke dashboard
validate: ; python -m runner.validate tasks/
test:     ; pytest -q
lint:     ; ruff check .
smoke:    ; for t in tasks/*/task.py; do for realism in lab wild; do inspect eval $$t -T realism=$$realism -T judge=mockllm/model --model mockllm/model --limit 2; done; done
dashboard: ; python -m analysis.dashboard results/gap_table.csv dashboard/index.html
