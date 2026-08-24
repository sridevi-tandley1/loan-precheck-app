"""
loan_rules.py — The Pre-Check rule engine (Agent 1's tool)
===========================================================
Deterministic, auditable, no API key needed. Every check maps 1:1 to
eligibility_rules.txt (R1–R8). The LLM never does this arithmetic —
it calls this engine as a TOOL. That separation is the design lesson:
language in the model, rules in code, decision with a human.

Training material for the iTNT Masterclass take-home. Synthetic data only.
"""

from dataclasses import dataclass, field

REQUIRED_DOCS = [
    "ID proof",
    "Address proof",
    "3 salary slips",
    "6-month bank statement",
]

@dataclass
class Applicant:
    applicant_id: str
    name: str
    age: int
    net_monthly_income_inr: float
    existing_emi_inr: float
    loan_amount_requested_inr: float
    tenure_months: int
    credit_score: int
    documents_submitted: list = field(default_factory=list)
    consistency_flag: bool = False   # True when any two facts contradict
    consistency_note: str = ""


def check(applicant: Applicant) -> dict:
    """Run all eight rules. Returns a dict ready to be printed as a card."""
    a = applicant
    checks, missing = {}, []

    # R5 — documents
    missing = [d for d in REQUIRED_DOCS if d not in a.documents_submitted]
    checks["R5 Documents"] = ("PASS", "All four documents present.") if not missing \
        else ("FAIL", f"Missing: {', '.join(missing)}")

    # R1 — age
    checks["R1 Age"] = ("PASS", f"{a.age} is within 21-60.") if 21 <= a.age <= 60 \
        else ("FAIL", f"{a.age} is outside 21-60.")

    # R2 — income
    checks["R2 Income"] = ("PASS", f"Rs {a.net_monthly_income_inr:,.0f} >= Rs 25,000.") \
        if a.net_monthly_income_inr >= 25000 \
        else ("FAIL", f"Rs {a.net_monthly_income_inr:,.0f} is below Rs 25,000.")

    # R3 — loan size
    cap = 20 * a.net_monthly_income_inr
    checks["R3 Loan size"] = ("PASS", f"Rs {a.loan_amount_requested_inr:,.0f} <= 20x income (Rs {cap:,.0f}).") \
        if a.loan_amount_requested_inr <= cap \
        else ("FAIL", f"Rs {a.loan_amount_requested_inr:,.0f} exceeds 20x income (Rs {cap:,.0f}).")

    # R4 — credit score bands
    if a.credit_score >= 700:
        checks["R4 Credit score"] = ("PASS", f"{a.credit_score} >= 700.")
    elif a.credit_score >= 650:
        checks["R4 Credit score"] = ("REVIEW", f"{a.credit_score} is in the 650-699 band.")
    else:
        checks["R4 Credit score"] = ("FAIL", f"{a.credit_score} is below 650.")

    # R6 — affordability (simplified EMI: amount / tenure, interest ignored — stated in rules)
    emi = a.loan_amount_requested_inr / a.tenure_months
    total = emi + a.existing_emi_inr
    limit = 0.5 * a.net_monthly_income_inr
    arithmetic = (f"{a.loan_amount_requested_inr:,.0f} / {a.tenure_months} = {emi:,.0f}; "
                  f"{emi:,.0f} + existing {a.existing_emi_inr:,.0f} = {total:,.0f} vs limit {limit:,.0f}")
    checks["R6 Affordability"] = ("PASS", arithmetic) if total <= limit else ("FAIL", arithmetic)

    # R7 — consistency
    checks["R7 Consistency"] = ("REVIEW", a.consistency_note or "Facts contradict — verify with applicant.") \
        if a.consistency_flag else ("PASS", "No contradictions found in the file.")

    # ---- Recommendation (priority order is the governance) ----
    if checks["R7 Consistency"][0] == "REVIEW":
        rec = f"NEEDS HUMAN REVIEW: {checks['R7 Consistency'][1]}"
    elif any(checks[r][0] == "FAIL" for r in ("R1 Age", "R2 Income", "R3 Loan size", "R6 Affordability")) \
            or checks["R4 Credit score"][0] == "FAIL":
        failed = [r for r in ("R1 Age", "R2 Income", "R3 Loan size", "R4 Credit score", "R6 Affordability")
                  if checks[r][0] == "FAIL"]
        rec = f"Not eligible at this time: {', '.join(failed)}"
    elif checks["R4 Credit score"][0] == "REVIEW":
        rec = "NEEDS HUMAN REVIEW: borderline credit score (650-699 band)"
    elif missing:
        rec = f"Collect first: {', '.join(missing)}; otherwise eligible for review"
    else:
        rec = "Ready for officer review"

    return {"applicant": a, "checks": checks, "missing": missing, "recommendation": rec}


def render_card(result: dict) -> str:
    a = result["applicant"]
    lines = [
        "LOAN PRE-CHECK CARD",
        f"Applicant: {a.name} ({a.applicant_id})",
        "",
        "1. DOCUMENTS: " + ("Complete" if not result["missing"]
                            else "Missing: " + ", ".join(result["missing"])),
        "2. RULE CHECKS:",
    ]
    for rule, (status, note) in result["checks"].items():
        lines.append(f"   {rule:<16} - {status:<6} - {note}")
    lines += [
        f"3. RECOMMENDATION: {result['recommendation']}",
        "",
        "This is a recommendation only. The loan officer decides.",
    ]
    return "\n".join(lines)
