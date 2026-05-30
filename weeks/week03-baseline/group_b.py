"""
group_b.py — Week 3–4 (Jun 2 – Jun 13, 2026)
Group B work stubs for the data preparation and baseline models sprint.
Covers dataset validation, a baseline or sanity-check script, and related work writing.
Owner: Group B -- Brian Stock, Noah Reed, Michael Castellano
"""

# TODO: Load and explore WSN-DS using Group A's loader
# - Run src/data/loader.py once available (or replicate minimal load logic here)
# - Confirm 374,661 rows, 18 features, 5 attack classes
# - Check class distribution — note imbalance between Normal and attack classes
# - Identify which features might be most relevant for mitigation rule thresholds

# TODO: Implement a baseline or validation script
# - Option A: train a simple Logistic Regression or Decision Tree on the dataset
#   using raw sklearn (independent of Group A's model wrappers) as a cross-check
# - Option B: write a dataset sanity-check script that validates column types,
#   expected value ranges, and attack class label spelling
# - Commit the chosen script to weeks/week03-04/

# TODO: Begin related-work section of the capstone report
# - Summarize 5–8 papers on wireless attack detection in WSN/UAV networks
# - Summarize 3–5 papers on FL-based intrusion detection systems
# - Summarize 3–5 papers on mitigation strategies for the four attack types
# - Draft the related-work section in a shared document or docs/ markdown file

# TODO: Refine UAV mission use case
# - Incorporate any feedback from Week 1–2 review with Dr. Hasan
# - Finalize network topology diagram (ASCII or drawn)
# - Define concrete "before-mitigation" and "after-mitigation" evaluation scenarios
