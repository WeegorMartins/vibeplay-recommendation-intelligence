import json
from pathlib import Path


data = json.loads(Path("dashboard/assets/dashboard_data.json").read_text(encoding="utf-8"))
failures = [x for x in data["governance"] if x["value"] < x["threshold"]]
if failures:
    raise SystemExit("Guardrail failure: " + ", ".join(x["check"] for x in failures))
print("All recommendation governance guardrails passed.")

