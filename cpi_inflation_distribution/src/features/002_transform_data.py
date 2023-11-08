import pandas as pd


data = pd.read_pickle("../../data/interim/nz_cpi_group_3_clean.pkl")

# --------------------------------------------------------------
# Transform data
# --------------------------------------------------------------

# Calculate annual percent change
cpi_data_apc=data.pct_change(periods=4) * 100

# --------------------------------------------------------------
# Export data
# --------------------------------------------------------------

cpi_data_apc.to_pickle("../../data/processed/nz_cpi_group_3_apc.pkl")
