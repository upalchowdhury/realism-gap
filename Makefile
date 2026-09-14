.PHONY: validate test lint smoke
validate: ; python -m runner.validate tasks/
test:     ; pytest -q
lint:     ; ruff check .
smoke:    ; for t in tasks/*/task.py; do for realism in lab wild; do inspect eval $$t -T realism=$$realism -T judge=mockllm/model --model mockllm/model --limit 2; done; done
