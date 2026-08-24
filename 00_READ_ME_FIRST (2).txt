# How this project was built — the prompt sequence

This repository is also a **teaching artifact**: it shows how each file was created through
plain-language prompts, in order. Nothing here required writing code from a blank page — every
file began as a specification handed to an AI assistant, then was run, tested, and corrected.
That loop — **specify → generate → run → test → fix** — is the whole method.

> **Read this alongside the code.** Each step gives the prompt, what came back, and how it was
> verified. Copy any prompt as a starting point for your own agent.

---

## The one principle behind every prompt

**The specification is the skill.** Every prompt below is really the same four blocks in prose —
**WHO** the code is for, the **STEPS** it performs, the **SHAPE** of its output, and the **RULES**
it must never break. The AI writes the syntax; you own the specification and the judgement.

---

## Step 1 — the decision engine (`loan_rules.py`)

**Why first:** the rules are the heart. Build and test them alone before any interface exists.

**Prompt used:**
```
Write a single Python file that checks a personal loan application against eight rules.
Represent an applicant as a dataclass with: id, name, age, net monthly income, existing EMI,
loan amount, tenure in months, credit score, a list of documents submitted, and a
consistency flag with a note.

The eight rules:
R1 age 21-60. R2 income >= 25000. R3 loan <= 20x income.
R4 credit score: >=700 PASS, 650-699 REVIEW, <650 FAIL.
R5 four required documents present. R6 affordability: (loan/tenure)+existing EMI <= 50% income,
and SHOW the arithmetic. R7 if the consistency flag is set, REVIEW. R8 the engine only
recommends; it never approves or rejects.

Return a dict with each rule's status and a one-line reason, plus a single recommendation
chosen by this priority: consistency REVIEW first, then any hard FAIL, then score-band REVIEW,
then collect-missing-documents, then "Ready for officer review". Add a render function that
prints a clean text card ending with "This is a recommendation only. The loan officer decides."
```

**What came back:** the dataclass, the `check()` function, and `render_card()`.
**How it was verified:** wrote five known cases (the golden set) and ran them — see Step 3.
**A real fix this produced:** the first version resolved a borderline applicant wrongly because
R7 wasn't given priority over the score band. The fix was one line — reordering the recommendation
logic — caught only because the golden set existed. *That is why you test.*

---

## Step 2 — the single-applicant runner (`agent1_precheck.py`)

**Prompt used:**
```
Using the engine in loan_rules.py, write a small command-line script that reads one applicant
(by id, default A002) from a CSV of synthetic applicants, runs the check, and prints the card.
Standard library only.
```
**Verified:** ran it against each id; output matched hand-worked expectations.

---

## Step 3 — the test harness (`test_golden_set.py`)

**Why it matters most:** this is how you *know* the engine works — and keep knowing it after every change.

**Prompt used:**
```
Write a test script with five cases and their expected recommendations:
A001 ready; A002 collect bank statement; A003 review (score 668); A006 not eligible (age 19);
A007 needs human review (income inconsistency). Run all five, print PASS/FAIL per case and a
summary line. Exit non-zero if any fail.
```
**Verified:** run `python test_golden_set.py` — all five must pass. Re-run after ANY edit to the rules.

---

## Step 4 — the batch scorer (`agent2_batch_scorer.py`)

**Prompt used:**
```
Extend the same engine: read the whole CSV of applicants, score each, and print the loan
officer's morning worklist in four groups — NEEDS HUMAN REVIEW first, then READY FOR REVIEW,
COLLECT ITEMS FIRST, NOT ELIGIBLE. Never move the review group down; unclear cases come first.
```
**Verified:** output showed 2 review / 1 ready / 1 collect / 4 not-eligible across the eight synthetic applicants — matched by hand.

---

## Step 5 — the ML caveat demo (`ml_model_caveat_demo.py`)

**Why it exists:** to prove, with numbers, that choosing the wrong model type hides real risk.

**Prompt used:**
```
Using scikit-learn, make a small synthetic credit dataset where debt burden only predicts
default IN COMBINATION with certain score ranges (a non-linear interaction). Train TWO models
on the same data: logistic regression and a random forest. Evaluate BOTH on a held-out split.
Report accuracy AND the percentage of actual defaulters each catches. Then show one borderline
applicant on which the two models give opposite verdicts. Print a one-line conclusion.
```
**What it showed:** accuracy 85.5% vs 86.6% (near-identical) but defaulters caught 15.9% vs 57.7%,
and opposite verdicts on one borderline applicant.
**The lesson:** accuracy alone lies; the model must fit the data's pattern. Coders run it;
everyone else carries the question *"who validated this model on our data's pattern?"*

---

## Step 6 — the web app, no-code hosting (`app.py`, Gradio)

**Prompt used:**
```
Convert the engine into a Gradio web app: one text box where a loan officer pastes an
application, one button, and the Pre-Check Card as output. Add a permanent banner:
"Training demo - synthetic data only. Do not enter real customer information."
Reuse loan_rules.py unchanged. Give me app.py and requirements.txt.
```
**Real fixes the run-test-fix loop produced (all normal, all instructive):**
- a wrong dataclass field name → caught on first run, renamed;
- a Gradio API change (`allow_flagging` → `flagging_mode`) → error message named it, one-word fix.
**Verified:** Priya's missing document flagged; A007 triggered NEEDS HUMAN REVIEW through the app's
own parser; junk input handled without a crash.

---

## Step 7 — the durable web app (`streamlit_app.py`, Streamlit)

**Prompt used:**
```
Convert the app to Streamlit, self-contained (import only from loan_rules.py, no Gradio).
Give it a styled interface for a Gen Z audience: a deep-navy background with a faint grid,
a bold display typeface, and the result rendered as a real "Pre-Check Card" with a colour-coded
verdict banner (green ready / amber review / blue collect / red not-eligible) and PASS/REVIEW/FAIL
status chips on each rule row. Keep a plain-text version in an expander for records. Keep the
synthetic-data banner. Requirements: just streamlit.
```
**Why self-contained mattered:** the first version imported from `app.py`, which would have
dragged Gradio into the Streamlit deployment for no reason. The fix was to inline the parser so
`streamlit_app.py` needs only `streamlit` + `loan_rules.py`.
**Verified:** rendered the correct card and chips for Priya (collect), A007 (review), A001 (ready);
no Gradio dependency pulled in.

---

## Step 8 — deployment (no code — configuration only)

No prompt writes this; it's clicks. See the README's **Deploy it yourself** section.
The lesson from deploying: platforms read filenames literally (`requirements.txt`, lowercase),
changing a Space's SDK needs a restart, and free tiers limit concurrent apps — none of which are
code problems, all of which are read-the-message-and-fix problems.

---

## The pattern to take away

Every file above followed the same five moves:

1. **Specify** in plain language — the four blocks in prose.
2. **Generate** with an AI assistant.
3. **Run** it.
4. **Test** against known-right answers (the golden set).
5. **Fix** by pasting the error back — one change at a time.

You never needed a blank editor and a memorised syntax. You needed a clear specification and the
discipline to test. *That* is the skill this repository teaches.

---

*Built for the Masterclass on Agentic AI @ Trichy · Dr. Sridevi Tandley · Siji Consultancy LLP.*
*All data synthetic. The agent recommends; a human decides.*
