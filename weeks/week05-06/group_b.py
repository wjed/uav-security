"""
group_b.py — Week 5–6 (Jun 16 – Jun 27, 2026)
Group B work stubs for the local learning and first FL prototype sprint.
Covers UAV scenario refinement and implementing initial mitigation rules.
Owner: Group B -- Brian Stock, Noah Reed, Michael Castellano
"""

# TODO: Refine UAV mission scenario
# - Incorporate feedback from Week 3–4 review with Dr. Hasan
# - Finalize: node count, flight path, topology, communication parameters
# - Clearly define what constitutes a "successful attack" and a "blocked attack" in the scenario
# - Document assumptions that differ from real UAV hardware (sim-to-real gap)

# TODO: Begin implementing src/mitigation/rules.py
# - Implement the rule dispatcher: look up countermeasure by predicted_class integer
# - Implement at least 2 rules with concrete actions:
#   - Blackhole (1): isolate node from routing table
#   - Flooding (4): apply rate-limiting
# - Stub remaining rules (Grayhole, TDMA) with placeholder logging

# TODO: Test mitigation pipeline with placeholder predictions
# - Use the sample fl_predictions.csv from Group A (or generate a synthetic version)
# - Run rules.py against it end-to-end
# - Confirm rule dispatcher correctly routes each class to the right action
# - Log actions taken to console or a results file

# TODO: Define before-mitigation baseline
# - Specify the "baseline" attack success rate in the UAV scenario (no mitigation applied)
# - Define the evaluation methodology for the after-mitigation comparison in Week 7–8
# - Document metric definitions in docs/ or the capstone report draft
