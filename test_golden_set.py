"""
ml_model_caveat_demo.py — THE CAVEAT, AS RUNNING CODE
=====================================================
When Agent 2 grows from rules to a machine-learning model, the model
must fit the DATA'S PATTERN. This demo proves it: the same synthetic
credit data, two models, materially different results — because the
true risk pattern is non-linear (an interaction between loan burden
and credit score), which a linear model cannot represent.

Banks call the discipline around this MODEL RISK MANAGEMENT:
independent validation, ongoing monitoring, clear ownership.

Run:  python ml_model_caveat_demo.py     (no API key needed)
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, accuracy_score

rng = np.random.default_rng(42)
N = 4000

income  = rng.uniform(20000, 90000, N)          # net monthly income
burden  = rng.uniform(0.05, 0.65, N)            # total EMI / income
score   = rng.uniform(600, 800, N)              # credit score

# TRUE risk pattern (non-linear, interaction): default is likely when a
# HIGH burden coincides with a MID-BAND score — not when either is alone.
p_default = 0.04 + 0.55 * ((burden > 0.45) & (score < 720)) \
                 + 0.20 * (income < 26000)
default = rng.random(N) < np.clip(p_default, 0, 0.95)

X = np.column_stack([income, burden, score])
Xtr, Xte, ytr, yte = train_test_split(X, default, test_size=0.3, random_state=7)

models = {
    "Logistic Regression (linear)": LogisticRegression(max_iter=2000),
    "Random Forest (non-linear)":   RandomForestClassifier(n_estimators=200, random_state=7),
}

print("Same data. Same split. Two models.\n" + "=" * 52)
results = {}
for name, m in models.items():
    m.fit(Xtr, ytr)
    pred = m.predict(Xte)
    rec = recall_score(yte, pred)      # of the true defaulters, how many caught
    acc = accuracy_score(yte, pred)
    results[name] = (rec, m)
    print(f"{name:<30} accuracy {acc:5.1%}   DEFAULTERS CAUGHT {rec:5.1%}")

# One borderline applicant, two opposite answers:
applicant = np.array([[48000, 0.52, 705]])   # decent income, heavy burden, mid score
print("\nOne borderline applicant  (income 48k, burden 52%, score 705):")
for name, (_, m) in results.items():
    verdict = "HIGH RISK" if m.predict(applicant)[0] else "low risk"
    print(f"  {name:<30} says: {verdict}")

print("""
THE CAVEAT, IN ONE SENTENCE:
  The linear model is confident, plausible — and blind to the pattern
  that actually predicts default. Same data, opposite decision.
  Choosing the model IS a risk decision. Validate the model against
  held-out data the way you validate an agent against a golden set —
  and in a bank, put it under Model Risk Management before any
  insight from it reaches a decision.
""")
