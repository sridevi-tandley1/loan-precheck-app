"""
streamlit_app.py — Loan Pre-Check demo as a Streamlit web app
=============================================================
TRAINING DEMO. Synthetic data only. The app recommends; a human decides.
Deploy on Streamlit Community Cloud (free): push this file + loan_rules.py
+ requirements_streamlit.txt (renamed to requirements.txt) to a GitHub repo,
then share.streamlit.io -> New app -> pick the repo -> main file streamlit_app.py.
"""
import streamlit as st
from loan_rules import Applicant, check, render_card
import re

FIELD_PATTERNS = {
    "applicant_id":  r"Applicant ID\s*:\s*(\S+)",
    "name":          r"Name\s*:\s*(.+)",
    "age":           r"Age\s*:\s*(\d+)",
    "income":        r"(?:Net monthly income|Income)\s*:\s*(?:Rs\.?\s*)?([\d,]+)",
    "existing_emi":  r"Existing EMIs?\s*:\s*(?:Rs\.?\s*)?([\d,]+|None)",
    "loan_amount":   r"Loan (?:requested|amount)\s*:\s*(?:Rs\.?\s*)?([\d,]+)",
    "tenure":        r"Tenure\s*:\s*(\d+)",
    "credit_score":  r"Credit score\s*:\s*(\d+)",
}
DOC_NAMES = ["ID proof", "Address proof", "Salary slips", "Bank statement"]
DOC_KEYS  = ["ID proof", "Address proof", "3 salary slips", "6-month bank statement"]

def _num(s):
    s = s.replace(",", "").strip()
    return 0 if s.lower() == "none" else int(s)

def parse_application(text):
    vals = {}
    for key, pat in FIELD_PATTERNS.items():
        m = re.search(pat, text, re.IGNORECASE)
        vals[key] = m.group(1).strip() if m else None
    docs = []
    for label, canon in zip(DOC_NAMES, DOC_KEYS):
        m = re.search(re.escape(label) + r".*?:\s*(YES|NO|NOT SUBMITTED)", text, re.IGNORECASE)
        if m and m.group(1).upper() == "YES":
            docs.append(canon)
    stated = re.search(r"stated income\s*(?:Rs\.?\s*)?([\d,]+)", text, re.IGNORECASE)
    slips  = re.search(r"slips average\s*(?:Rs\.?\s*)?([\d,]+)", text, re.IGNORECASE)
    flag, note = False, ""
    if stated and slips and _num(stated.group(1)) != _num(slips.group(1)):
        flag = True
        note = f"Stated income {stated.group(1)} but slips average {slips.group(1)} - verify"
    return Applicant(
        applicant_id=vals["applicant_id"] or "UNKNOWN",
        name=vals["name"] or "UNCLEAR",
        age=int(vals["age"]) if vals["age"] else None,
        net_monthly_income_inr=_num(vals["income"]) if vals["income"] else None,
        existing_emi_inr=_num(vals["existing_emi"]) if vals["existing_emi"] is not None else 0,
        loan_amount_requested_inr=_num(vals["loan_amount"]) if vals["loan_amount"] else None,
        tenure_months=int(vals["tenure"]) if vals["tenure"] else None,
        credit_score=int(vals["credit_score"]) if vals["credit_score"] else None,
        documents_submitted=docs,
        consistency_flag=flag,
        consistency_note=note,
    )

def precheck(application_text):
    if not application_text or len(application_text.strip()) < 40:
        return ("Paste a full application (use application_priya.txt from the "
                "sample pack as the format).")
    try:
        return render_card(check(parse_application(application_text)))
    except Exception as e:
        return f"Could not read the application: {e}\nCheck the format against the sample file."


st.set_page_config(page_title="Loan Pre-Check — training demo", page_icon="🏦")

st.title("🏦 Loan Pre-Check — Agent 1 (training demo)")
st.warning(
    "**Synthetic data only. Do not enter real customer information.** "
    "This tool recommends; the loan officer decides."
)

application_text = st.text_area(
    "Paste one loan application (synthetic sample from the pack)",
    height=340,
    placeholder="Applicant ID : A002\nName : Priya Shanmugam\nAge : 28\n...",
)

if st.button("Run pre-check", type="primary"):
    st.text(precheck(application_text))

st.caption(
    "Dr. Sridevi Tandley · Siji Consultancy LLP — Masterclass companion · iTNT Hub, Trichy"
)
