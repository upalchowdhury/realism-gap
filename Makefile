.PHONY: validate test lint smoke
validate: ; python -m runner.validate tasks/
test:     ; pytest -q
lint:     ; ruff check .
smoke:    ; for t in tasks/*/task.py; do inspect eval $$t --model mockllm/model --limit 2; done
