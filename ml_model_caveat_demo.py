"""
agent1_precheck.py — Agent 1: the Loan Pre-Check (offline reference build)
==========================================================================
Runs the Pre-Check Card for one applicant. This is the deterministic
version — same logic the LLM notebook calls as a tool.

Run:  python agent1_precheck.py            (checks Priya, A002)
      python agent1_precheck.py A007       (any applicant from the CSV)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loan_rules import check, render_card
from agent2_batch_scorer import load_applicants

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "A002"
    apps = {a.applicant_id: a for a in load_applicants()}
    if target not in apps:
        print(f"Unknown applicant id {target}. Known: {', '.join(apps)}"); sys.exit(1)
    print(render_card(check(apps[target])))
