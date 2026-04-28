"""RUN-045 natural viability-kernel elimination entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .proof_action_natural_viability_kernel import run_natural_viability_kernel_elimination
from .utils import load_yaml


def run_natural_viability_kernel_elimination_from_config(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_yaml(config_path) if config_path else {}
    return run_natural_viability_kernel_elimination(cfg, out=out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_natural_viability_kernel_elimination_from_config(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
