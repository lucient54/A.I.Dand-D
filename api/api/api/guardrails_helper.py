# api/guardrails_helper.py
# Optional: Guardrails integration for auto-repair of malformed outputs.

try:
    from guardrails import Guard
    HAS_GUARDRAILS = True
except Exception:
    HAS_GUARDRAILS = False

RAIL_SPEC_PATH = "api/dm_output.guardspec"  # you can create this file if you want to use Guardrails

def attempt_guardrails_repair(raw_text: str):
    if not HAS_GUARDRAILS:
        raise RuntimeError("Guardrails not installed. pip install guardrails-ai")
    guard = Guard.from_rail(RAIL_SPEC_PATH)
    validated, *_ = guard(llm_output=raw_text, num_reasks=2)
    return validated
