"""
streamlit_app.py — Loan Pre-Check demo (Agent 1) as a styled Streamlit web app
==============================================================================
TRAINING DEMO. Synthetic data only. The app recommends; a human decides.

Deploy on Streamlit Community Cloud (free):
push this file + loan_rules.py + requirements.txt to a public GitHub repo,
then share.streamlit.io -> Create app -> pick the repo -> main file streamlit_app.py.

The visual layer is custom CSS injected below; the decision logic is 100% the
same validated engine in loan_rules.py — the UI never computes eligibility.
"""
import re
import streamlit as st
from loan_rules import Applicant, check, render_card

# ----------------------------------------------------------------------------
# Application parser (same validated logic as the Gradio app)
# ----------------------------------------------------------------------------
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

SAMPLE = """Applicant ID : A002
Name : Priya Shanmugam
Age : 28
Net monthly income : Rs 38,000
Existing EMIs : None
Loan requested : Rs 4,50,000
Tenure : 36 months
Credit score : 715
Documents submitted:
1. ID proof - PAN card : YES
2. Address proof - Aadhaar : YES
3. Salary slips (3 months) : YES
4. Bank statement (6 months) : NOT SUBMITTED"""

# ----------------------------------------------------------------------------
# Page + custom visual layer
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Loan Pre-Check Agent", page_icon="🏦", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

/* ambient decision-desk background: deep navy with a faint grid */
.stApp {
  background:
    radial-gradient(1200px 600px at 20% -10%, #123456 0%, transparent 55%),
    radial-gradient(1000px 500px at 110% 10%, #0d2a47 0%, transparent 50%),
    #0A2540;
  background-attachment: fixed;
}
.stApp::before{
  content:""; position:fixed; inset:0; pointer-events:none; opacity:.35;
  background-image:linear-gradient(#ffffff10 1px,transparent 1px),linear-gradient(90deg,#ffffff10 1px,transparent 1px);
  background-size:44px 44px;
}
.block-container{padding-top:2.4rem; max-width:820px;}

/* hero */
.hero-kicker{font-family:'Space Grotesk',sans-serif;letter-spacing:.42em;font-size:.72rem;
  color:#F5871F;font-weight:700;text-transform:uppercase;}
.hero-title{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:2.7rem;line-height:1.05;
  color:#F2F6FB;margin:.2rem 0 .1rem;}
.hero-title .arrow{color:#F5871F;}
.hero-sub{font-family:'Inter',sans-serif;color:#93A9C2;font-size:1.02rem;margin-bottom:1.1rem;}

/* privacy banner */
.privacy{display:flex;gap:.7rem;align-items:flex-start;background:rgba(245,135,31,.10);
  border:1px solid rgba(245,135,31,.5);border-radius:14px;padding:.8rem 1rem;margin:.2rem 0 1.4rem;}
.privacy b{color:#FFB25C;} .privacy span{font-family:'Inter';color:#C6D6E8;font-size:.92rem;line-height:1.5;}

/* input area */
.stTextArea textarea{background:#071A30 !important;color:#E8F0FA !important;
  border:1.5px solid #234a74 !important;border-radius:14px !important;font-family:'JetBrains Mono',monospace !important;
  font-size:.9rem !important;}
.stTextArea textarea:focus{border-color:#F5871F !important;box-shadow:0 0 0 2px rgba(245,135,31,.25) !important;}
.stTextArea label{color:#93A9C2 !important;font-family:'Inter';font-weight:600;}

/* buttons */
.stButton>button{background:#F5871F;color:#0A2540;font-family:'Space Grotesk',sans-serif;font-weight:700;
  border:none;border-radius:12px;padding:.6rem 1.6rem;font-size:1rem;transition:transform .08s,box-shadow .2s;}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(245,135,31,.35);color:#0A2540;}

/* result card */
.card{background:linear-gradient(180deg,#0d2137,#071A30);border:1.5px solid #234a74;border-radius:20px;
  padding:1.5rem 1.6rem;margin-top:1.4rem;box-shadow:0 20px 60px rgba(0,0,0,.45);
  animation:rise .5s cubic-bezier(.2,.9,.3,1.2) both;}
@keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.card-head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1d3a5c;
  padding-bottom:.9rem;margin-bottom:1rem;}
.card-title{font-family:'Space Grotesk';font-weight:700;color:#F2F6FB;font-size:1.15rem;}
.card-id{font-family:'JetBrains Mono';color:#93A9C2;font-size:.85rem;}

/* verdict banner */
.verdict{border-radius:14px;padding:1rem 1.2rem;margin-bottom:1.1rem;font-family:'Space Grotesk';font-weight:700;
  font-size:1.05rem;display:flex;align-items:center;gap:.7rem;}
.verdict.ready{background:rgba(53,194,126,.14);border:1.5px solid #35C27E;color:#7EE6B0;}
.verdict.review{background:rgba(245,178,92,.14);border:1.5px solid #FFB25C;color:#FFC98A;}
.verdict.collect{background:rgba(90,150,220,.14);border:1.5px solid #6AA6E8;color:#A8CCF2;}
.verdict.no{background:rgba(232,96,76,.14);border:1.5px solid #E8604C;color:#F09E90;}
.verdict small{display:block;font-family:'Inter';font-weight:500;font-size:.82rem;opacity:.85;margin-top:.15rem;}

/* rule rows */
.rule{display:flex;align-items:center;gap:.8rem;padding:.55rem 0;border-bottom:1px solid #12304e;}
.rule:last-child{border-bottom:none;}
.chip{font-family:'JetBrains Mono';font-weight:700;font-size:.68rem;letter-spacing:.05em;padding:.2rem .55rem;
  border-radius:6px;min-width:66px;text-align:center;}
.chip.PASS{background:rgba(53,194,126,.18);color:#7EE6B0;}
.chip.REVIEW{background:rgba(255,178,92,.18);color:#FFC98A;}
.chip.FAIL{background:rgba(232,96,76,.18);color:#F09E90;}
.rule-name{font-family:'Inter';font-weight:600;color:#E8F0FA;font-size:.9rem;min-width:130px;}
.rule-note{font-family:'Inter';color:#93A9C2;font-size:.84rem;line-height:1.4;}

/* footer line inside card */
.decides{margin-top:1.1rem;padding-top:.9rem;border-top:1px dashed #234a74;font-family:'Inter';
  color:#FFB25C;font-weight:600;font-size:.9rem;text-align:center;}

.credit{font-family:'Inter';color:#5f7592;} /* placeholder overwritten below */
footer, #MainMenu, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-kicker">iTNT Hub · Masterclass companion</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Loan Pre-Check <span class="arrow">Agent</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Paste one loan application. Get a structured Pre-Check Card in seconds — documents, eight rules, and a recommendation.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="privacy">
  <b>⚠</b><span><b>Synthetic data only — do not enter real customer information.</b>
  This is a training demo. Aadhaar, passwords or any real applicant's details never go into an AI tool.
  The agent recommends; a loan officer decides.</span>
</div>""", unsafe_allow_html=True)

VERDICT_CLASS = {"Ready": "ready", "NEEDS": "review", "Collect": "collect", "Not eligible": "no"}
def verdict_class(rec):
    for k, c in VERDICT_CLASS.items():
        if rec.startswith(k):
            return c
    return "review"

def render_rich(result):
    a = result["applicant"]
    rec = result["recommendation"]
    vc = verdict_class(rec)
    label = {"ready":"READY FOR OFFICER REVIEW","review":"NEEDS HUMAN REVIEW",
             "collect":"COLLECT ITEMS FIRST","no":"NOT ELIGIBLE AT THIS TIME"}[vc]
    detail = rec.split(":",1)[1].strip() if ":" in rec else ""
    rows = ""
    for rule, (status, note) in result["checks"].items():
        rows += (f'<div class="rule"><span class="chip {status}">{status}</span>'
                 f'<span class="rule-name">{rule}</span>'
                 f'<span class="rule-note">{note}</span></div>')
    docs = "Complete" if not result["missing"] else "Missing: " + ", ".join(result["missing"])
    st.markdown(f"""
<div class="card">
  <div class="card-head">
    <span class="card-title">🏦 Pre-Check Card</span>
    <span class="card-id">{a.name} · {a.applicant_id}</span>
  </div>
  <div class="verdict {vc}">✦ {label}<small>{detail}</small></div>
  <div class="rule"><span class="chip {'PASS' if not result['missing'] else 'FAIL'}">DOCS</span>
    <span class="rule-name">Documents</span><span class="rule-note">{docs}</span></div>
  {rows}
  <div class="decides">This is a recommendation only. The loan officer decides.</div>
</div>""", unsafe_allow_html=True)

app_text = st.text_area("Loan application (synthetic sample from the pack)", value=SAMPLE, height=280)
c1, c2 = st.columns([1, 3])
run = c1.button("Run pre-check")

if run:
    if not app_text or len(app_text.strip()) < 40:
        st.info("Paste a full application — use the sample above as the format.")
    else:
        try:
            with st.spinner("Reading the application and checking eight rules…"):
                result = check(parse_application(app_text))
            render_rich(result)
            with st.expander("Plain-text card (copy for records)"):
                st.code(render_card(result), language="text")
        except Exception as e:
            st.error(f"Could not read the application: {e}\nCheck the format against the sample.")

st.markdown('<div style="text-align:center;margin-top:2rem;font-family:Inter;color:#5f7592;font-size:.8rem">'
            'Dr. Sridevi Tandley · Siji Consultancy LLP — Masterclass companion · iTNT Hub, Trichy</div>',
            unsafe_allow_html=True)
