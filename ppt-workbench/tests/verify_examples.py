"""Maintainer tool: inspect and render paired synthetic examples; no model evaluation claims."""

import argparse
import json
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--soffice", help="Opt in to the optional LibreOffice preview route")
    args = parser.parse_args()
    root = args.skill_dir.resolve()
    sys.path.insert(0, str(root / "scripts"))
    from inspect_pptx import inspect
    if args.soffice:
        sys.path.insert(0, str(root / "scripts/optional"))
        from render_with_libreoffice import render
    output = root / "assets/examples/output"
    cases = json.loads((root / "assets/examples/cases.json").read_text(encoding="utf-8"))
    results = []
    for case in cases:
        started = time.monotonic()
        pptx = output / (case["id"] + ".pptx")
        try:
            report = inspect(pptx)
            if report["errors"]:
                raise ValueError("; ".join(report["errors"]))
            page = report["pages"][0]
            for kind in case["expected"]:
                field = {"text":"texts", "shape":"native_shapes", "table":"tables", "chart":"charts", "image":"pictures"}[kind]
                if not page[field]:
                    raise ValueError(f"Missing requested {kind}")
            preview = output / case["id"]
            if preview.exists():
                record = json.loads((preview / "render.json").read_text())
                if record["source_sha256"] != report["sha256"]:
                    raise ValueError("Stale preview; use a fresh output directory after regeneration")
            elif args.soffice:
                record = render(pptx, preview, soffice=args.soffice)
            else:
                record = None
            if preview.exists():
                report["file"] = pptx.name
                (preview / "objects.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            result = {"case":case["id"],"structure":"pass","render":"pass" if record else "not_performed","sha256":report["sha256"],
                      "renderer":record["renderer"] if record else None,"seconds":round(time.monotonic()-started,3),"visual_review":"pending"}
        except Exception as exc:
            result = {"case":case["id"],"structure_or_render":"fail","reason":str(exc),"seconds":round(time.monotonic()-started,3)}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    summary = {"kind":"deterministic_tool_smoke", "model_independent_repeats":"not_performed",
               "powerpoint_roundtrip":"not_performed", "results":results}
    (output / "verification.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return 0 if all(r.get("structure")=="pass" for r in results) else 2


if __name__ == "__main__":
    sys.exit(main())
