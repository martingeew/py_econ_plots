import pandas as pd

# --------------------------------------------------------------
# 1. Define objective
# --------------------------------------------------------------

""" 
The objective of this script is to clean the dataset of the cpi data, set the index, and enforce the correct data type.

"""

# --------------------------------------------------------------
# 2. Read raw data
# --------------------------------------------------------------

# Loading all the datasets using the provided format
cpi_data = pd.read_csv('../../data/raw/nz_cpi_subgroup_2_2023q4.csv', sep=',')


# --------------------------------------------------------------
# 3. Process data
# --------------------------------------------------------------

# Replace the ".." string with NaN to mark missing values
cpi_data.replace('..', pd.NA, inplace=True)

# Remove any rows that are entirely NaN, which likely correspond to metadata or contact info
cpi_data.dropna(how='all', inplace=True)

# Rename index
cpi_data.rename(columns={'Unnamed: 0': 'Quarter'}, inplace=True)

# Set the 'Quarter' column as the index of your DataFrame for plotting
cpi_data.set_index('Quarter', inplace=True)

# Convert data to numeric, ignoring errors to bypass non-numeric data
cpi_data = cpi_data.apply(pd.to_numeric, errors='coerce')

# --------------------------------------------------------------
# Export
# --------------------------------------------------------------

cpi_data.to_pickle("../../data/interim/nz_cpi_group_3_clean_2023q4.pkl")
