"""
group_b.py — Week 1–2 (May 18 – May 30, 2026)
Group B work stubs for the project setup and background review sprint.
Covers UAV attack literature review and drafting the mission use case.
Owner: Group B -- Brian Stock, Noah Reed, Michael Castellano
"""

# TODO: Literature review — UAV network attacks and jamming
# - Review papers on UAV communication vulnerabilities and wireless attack scenarios
# - Focus on Blackhole and Grayhole routing attacks in multi-hop UAV networks
# - Review TDMA disruption and Flooding-based denial-of-service in aerial networks
# - Note how attack behavior differs in UAV vs. ground WSN contexts

# TODO: Literature review — mitigation strategies
# - Survey rule-based and ML-assisted mitigation approaches for UAV network attacks
# - Identify which attack classes allow automated countermeasures vs. require human review
# - Review existing before-and-after evaluation frameworks for network security tools

# TODO: Draft UAV mission use case
# - Define the mission scenario: UAV roles (data relay, surveillance, coordination), flight path
# - Define network topology: how UAV nodes communicate, which node plays coordinator
# - Specify what a "successful attack" looks like in this scenario (e.g., data loss, route failure)
# - Draft communication assumptions: protocol layer, packet structure, link model

# TODO: Coordinate with Group A on prediction handoff format
# - Review Group A's planned output format for results/fl_predictions.csv
# - Confirm columns needed by src/mitigation/rules.py: node_id, predicted_class, confidence_score
# - Document any additional fields needed for mitigation rule evaluation
