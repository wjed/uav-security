"""
download_data.py
Instructions and helper script for downloading the WSN-DS dataset from Kaggle
and placing it in the correct data/raw/ directory.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (os, pathlib, sys, subprocess)

# TODO: Print dataset download instructions
# - Display Kaggle dataset URL: https://www.kaggle.com/datasets/bassamkasasbeh1/wsnds
# - Remind user to place WSN-DS.csv in data/raw/
# - Warn that data/raw/ is gitignored — never commit the CSV

# TODO: Check if Kaggle CLI is available
# - Run: kaggle --version
# - If available, offer automated download
# - If not, print manual instructions and exit

# TODO: Automated download via Kaggle CLI (optional)
# - Run: kaggle datasets download -d bassamkasasbeh1/wsnds --path data/raw/ --unzip
# - Verify WSN-DS.csv is present at data/raw/WSN-DS.csv after extraction

# TODO: Validate downloaded file
# - Check expected row count (~374,661 rows)
# - Check expected column count (18 features + Attack type label)
# - Print confirmation message or raise informative error with remediation steps
