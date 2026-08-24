FOLDER 03 — CODE PACK (Paths B & C)
===================================
New here? Read these two first (they are .md files - open in
any text editor, or on GitHub for nice formatting):
  README.md            -> what every file is + how to deploy
  HOW_IT_WAS_BUILT.md  -> the exact prompts that created each
                          file. Copy them to build your own.
                          This file IS the vibe-coding lesson.

The engine (plain Python, nothing to install):
  loan_rules.py          the 8 rules as auditable code
  agent1_precheck.py     pre-check one applicant
  agent2_batch_scorer.py the officer's morning worklist
  test_golden_set.py     RUN THIS FIRST -> "ALL 5 TESTS PASS"
  loan_applications.csv  8 synthetic applicants

The web apps (for folder 04):
  app.py + requirements.txt      Gradio version (Hugging Face)
  streamlit_app.py               Streamlit version (styled)

The caveat, live:
  ml_model_caveat_demo.py  Two ML models, same data, opposite
      verdicts. Run before you ever replace rules with a model.
      Non-coders: skip the file, keep the question it teaches —
      "who validated this model on our data's pattern?"

Going deeper (Google Colab, free API key needed):
  Build_4_Loan_PreCheck_Agent.ipynb  the fully agentic version
  Build_1..3 + student_guide.md      RAG, ReAct, multi-agent
