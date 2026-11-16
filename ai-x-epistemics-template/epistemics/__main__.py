"""Command line: run a study, or check the report against its claims."""

from __future__ import annotations

import sys

from epistemics.check import check_submission, format_result
from epistemics.client import load_dotenv
from epistemics.run import find_root
from epistemics.studies import STUDIES

HELP = """Usage:
  python -m epistemics run <fliprate|citation_binder|crux_mapper|notes_delay|commute|premises|all>
  python -m epistemics check

An empty MODEL_API_KEY uses the committed fixtures. Copy .env.example to .env to call a model.
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = find_root()
    load_dotenv(root / ".env")
    if not args or args[0] in {"-h", "--help", "help"}:
        print(HELP.strip())
        return 0
    command = args[0]
    if command == "check":
        result = check_submission(root)
        print(format_result(result))
        return 0 if result.ok else 1
    if command == "run":
        if len(args) != 2:
            print(HELP.strip())
            return 2
        name = args[1]
        names = [item for item in STUDIES if item not in ("commute", "premises")] if name == "all" else [name]
        unknown = [item for item in names if item not in STUDIES]
        if unknown:
            print(f"Unknown study: {unknown[0]}")
            print(HELP.strip())
            return 2
        for study in names:
            payload = STUDIES[study](root)
            metrics = payload["metrics"]
            print(f"Wrote results/{payload['study']}.json provider={payload['provider']} model={payload['model']} metrics={metrics}")
        return 0
    print(HELP.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
