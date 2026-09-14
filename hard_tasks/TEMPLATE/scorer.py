"""Hidden scorer. Never copied into the agent's container.

Contract: run from the task root after the agent finishes; print one JSON object to stdout.
"""

import json
import subprocess
import sys


def main() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests_hidden", "-q", "--no-header"],
        capture_output=True,
        text=True,
    )
    passed = proc.returncode == 0
    print(json.dumps({"score": 1 if passed else 0, "partial": {}, "notes": proc.stdout[-2000:]}))


if __name__ == "__main__":
    main()
