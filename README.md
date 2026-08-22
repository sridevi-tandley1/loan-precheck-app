# 🏦 Loan Pre-Check Agent — Agentic AI Masterclass (iTNT Hub, Trichy)

A no-code / low-code **Agentic AI** demo: paste one loan application, get a structured
**Pre-Check Card** — documents checked, eight eligibility rules applied, and a clear
recommendation. **The agent recommends; a loan officer decides.**

> ⚠️ **Training demo. Synthetic data only.** Every applicant here is invented.
> Never put real customer data — Aadhaar, passwords, real applicant details — into any AI tool.

**Live app:** deploy your own in ~10 minutes using the steps below. No payment, no credit card.

---

## What each file is

| File | What it is | Do I edit it? |
|---|---|---|
| `streamlit_app.py` | **The web app.** The styled interface + the text parser. Reads the pasted application, calls the rule engine, and draws the Pre-Check Card. | No — just deploy it |
| `loan_rules.py` | **The decision engine.** The eight eligibility rules as plain, auditable Python. This is what actually decides PASS / REVIEW / FAIL — the app never decides on its own. | Only to change the rules |
| `requirements.txt` | **The shopping list.** Tells the hosting platform which Python packages to install (just `streamlit`). Must be named exactly this — lowercase. | No |
| `README.md` | This file. | — |
| `HOW_IT_WAS_BUILT.md` | **The prompt story.** The exact plain-language prompts that created each file, in order — copy them to build your own. | Read it |

**The design idea in one line:** *language and layout live in the app; the rules live in the engine; the decision stays with a human.* That separation is the whole lesson — you can read `loan_rules.py` and audit every rule, which you could never do with a black-box model.

---

## How this was built (and how you build the same way)

**Nothing here was written from a blank page.** Every file started as a plain-language prompt
handed to an AI assistant, then was run, tested, and corrected. The full prompt-by-prompt story —
copy-paste ready — is in **[`HOW_IT_WAS_BUILT.md`](HOW_IT_WAS_BUILT.md)**. The short version:

1. **`loan_rules.py`** — prompt: "check a loan application against these eight rules, return each
   rule's status + a recommendation, never approve/reject." *(The decision engine — built first.)*
2. **`test_golden_set.py`** — prompt: "five test cases with expected answers; pass/fail each."
   *(How you know it works — and a real bug in the rules was caught here.)*
3. **`agent1_precheck.py` / `agent2_batch_scorer.py`** — prompt: "run one applicant" / "score the
   whole CSV into a ranked worklist." *(One agent, then the batch.)*
4. **`ml_model_caveat_demo.py`** — prompt: "two models on the same data; report accuracy AND
   defaulters caught; show a case where they disagree." *(Proves why model choice is a risk decision.)*
5. **`app.py`** — prompt: "convert the engine into a Gradio web app with a privacy banner."
6. **`streamlit_app.py`** — prompt: "convert to a styled, self-contained Streamlit app with a
   colour-coded Pre-Check Card." *(The deployed version.)*

Every step was the same loop: **specify → generate → run → test → fix.** The AI writes the syntax;
you own the specification and the testing. That is the skill — not memorising code.

---

## Deploy it yourself — Streamlit Community Cloud (free, ~10 minutes)

You need two free accounts: **GitHub** (stores the code) and **Streamlit** (runs it). No card, ever.

### Step 1 — Get the code into your own GitHub
1. Create a free account at **github.com**.
2. Click **New** (green button) → name the repo `loan-precheck-app` → set **Public** → **Create repository**.
3. On the empty repo page: **Add file → Upload files**.
4. Upload these three files: `streamlit_app.py`, `loan_rules.py`, `requirements.txt`.
   - ⚠️ The requirements file **must be named exactly `requirements.txt`** — all lowercase. `Requirements.txt` or `requirements_streamlit.txt` will fail silently.
5. Click **Commit changes**.

### Step 2 — Deploy on Streamlit
6. Go to **share.streamlit.io** → **Continue with GitHub** → **Authorize** (one-time; approve the permission to read your repos).
7. Click **Create app → Deploy a public app from GitHub**.
8. Fill in:
   - **Repository:** `your-username/loan-precheck-app`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
9. Click **Deploy**. First build takes 1–3 minutes.
10. You get a permanent URL like `https://loan-precheck-app-xxxx.streamlit.app` — share it with anyone.

### Step 3 — Test before you trust (do this every time you deploy)
Paste each case, press **Run pre-check**, confirm the result:

| Test | Paste | Correct result |
|---|---|---|
| **A — missing document** | The Priya sample (loads by default) | **COLLECT ITEMS FIRST** — missing 6-month bank statement |
| **B — the stop test** | The Suresh block below | **NEEDS HUMAN REVIEW** — income inconsistency |
| **C — junk input** | just type `hello` | A polite "paste a full application" message, no crash |

<details>
<summary>Suresh test block (copy this for Test B)</summary>

```
Applicant ID : A007
Name : Suresh Babu
Age : 38
Net monthly income : Rs 60,000
Existing EMIs : Rs 8,000
Loan requested : Rs 8,00,000
Tenure : 48 months
Credit score : 755
1. ID proof : YES
2. Address proof : YES
3. Salary slips : YES
4. Bank statement : YES
Note: stated income Rs 60,000 but slips average Rs 32,000
```
Test B is the one that matters: if the app scores Suresh instead of stopping, it has failed —
an agent that quietly picks one number when the facts contradict is dangerous, however confident it looks.
</details>

Three greens = your deployment is real and shareable.

---

## Common problems and their fixes

| What you see | What it means | Fix |
|---|---|---|
| `ModuleNotFoundError: streamlit` | The requirements file wasn't found | Rename it to exactly `requirements.txt` (lowercase), commit, reboot the app |
| App shows a stack trace | A file is missing or misnamed | Confirm all three files are in the repo root, spelled exactly as above |
| `403 — quota limit` (Hugging Face) | Too many apps running on one account | Not a paywall — pause other apps, or use Streamlit as here |
| Repo doesn't appear in Streamlit | Streamlit wasn't authorised to read it, or repo is private | Re-authorise on share.streamlit.io; set the repo **Public** |
| Blank / "in the oven" | First boot | Wait ~1 minute; it self-starts |

---

## The eight rules (in `loan_rules.py`)

`R1` age 21–60 · `R2` income ≥ ₹25,000 · `R3` loan ≤ 20× income · `R4` credit score
(≥700 pass / 650–699 review / <650 fail) · `R5` four required documents ·
`R6` affordability (EMI + existing EMIs ≤ 50% of income) · `R7` consistency
(contradictions → human review) · `R8` authority — **the agent recommends; a human decides.**

---

## Free alternatives if you don't want GitHub

- **72-hour link (zero accounts):** run the pack's `app.py` in Google Colab with
  `app.demo.launch(share=True)` — Gradio gives a temporary public `*.gradio.live` URL.
- **Hugging Face Spaces:** upload `app.py` + `loan_rules.py` + `requirements.txt`, SDK = Gradio.

---

*Built for the Masterclass on Agentic AI @ Trichy · Dr. Sridevi Tandley · *
*All data synthetic. The agent recommends; a human decides.*
