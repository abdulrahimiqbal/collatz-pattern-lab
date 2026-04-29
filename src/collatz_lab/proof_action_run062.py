"""RUN-062 final theorem gate."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .proof_action_parametric_entry_coverage import REPO_ROOT, read_json, write_json
from .utils import load_yaml


RUN_ID = "RUN-062-certified-bundle-soundness-final-theorem"


def _copy_to_store(name: str, path: Path) -> Path:
    store = REPO_ROOT / "certificate_store"
    store.mkdir(parents=True, exist_ok=True)
    dst = store / f"run062_{name}{''.join(path.suffixes)}"
    shutil.copy2(path, dst)
    return dst


def run_final_theorem_gate(config_path: str | Path | None = None, *, out: str | Path | None = None) -> dict:
    cfg = load_yaml(config_path) if config_path else {}
    run_cfg = cfg.get("final_theorem_gate_run062", {}) if isinstance(cfg.get("final_theorem_gate_run062"), dict) else {}
    out_dir = Path(out or run_cfg.get("out_dir") or f"reports/runs/{RUN_ID}")
    out_dir.mkdir(parents=True, exist_ok=True)
    run061_path = Path(run_cfg.get("run061_result") or "certificate_store/run061_run_result.json")
    run061 = read_json(run061_path) if run061_path.exists() else {}
    ready = run061.get("formalization_status") == "GLOBAL_LEAN_SEMANTICS_COMPLETE"
    status = "RUN051_DESCENT_FORMALIZED" if ready else "FINAL_THEOREM_BLOCKED"
    gaps = [] if ready else [run061.get("formalization_status", "RUN061_RESULT_MISSING")]
    status_out = out_dir / "formalization_status.json"
    gaps_out = out_dir / "missing_final_theorem_gaps.md"
    run_result_out = out_dir / "run_result.json"
    write_json(
        {
            "schema": "collatz_lab.run062_formalization_status",
            "version": 1,
            "run_id": RUN_ID,
            "status": status,
            "checkCertifiedSystemBundle_sound": ready,
            "run051_descent": ready,
            "collatz_conjecture": ready,
        },
        status_out,
    )
    gaps_out.write_text("# RUN-062 Final Theorem Gate\n\n" + "\n".join(f"- `{gap}`" for gap in gaps) + "\n", encoding="utf-8")
    result = {
        "schema": "collatz_lab.run062_final_theorem_gate",
        "version": 1,
        "run_id": RUN_ID,
        "status": "PASS" if ready else "FAIL",
        "formalization_status": status,
        "training_launched": False,
        "search_launched": False,
        "gaps": gaps,
        "artifacts": {
            "formalization_status": str(status_out),
            "missing_final_theorem_gaps": str(gaps_out),
            "run_result": str(run_result_out),
        },
    }
    write_json(result, run_result_out)
    store_result = _copy_to_store("run_result", run_result_out)
    result["artifacts"]["certificate_store_run_result"] = str(store_result)
    write_json(result, run_result_out)
    shutil.copy2(run_result_out, store_result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run_final_theorem_gate(args.config, out=args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
