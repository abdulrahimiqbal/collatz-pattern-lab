"""RUN-038E exact SCC refinement and invariant discovery entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .proof_action_scc_refinement_invariant_discovery import run_scc_refinement_invariant_discovery
from .utils import load_yaml


def run_scc_refinement_invariant_discovery_from_config(
    config_path: str | Path | None = None,
    *,
    out: str | Path | None = None,
) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    return run_scc_refinement_invariant_discovery(cfg, out=out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_scc_refinement_invariant_discovery_from_config(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
