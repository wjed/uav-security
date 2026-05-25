"""
loader.py
Loads and validates the WSN-DS dataset from the configured raw data path.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (pandas, pathlib, yaml)

# TODO: Load configuration from config/config.yaml
# - Read data.raw_path setting

# TODO: Load WSN-DS.csv into a DataFrame
# - Strip leading/trailing whitespace from all column names
# - Strip leading/trailing whitespace from all Attack type label string values
# - Validate all 18 expected feature columns are present
# - Validate 'Attack type' label column is present
# - Drop the 'id' column if present
# - Return clean DataFrame

# TODO: Raise informative FileNotFoundError if CSV is not found
# - Print the expected path
# - Direct user to run data/download_data.py or visit the Kaggle URL
