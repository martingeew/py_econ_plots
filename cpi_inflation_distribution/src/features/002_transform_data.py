import pandas as pd


data = pd.read_pickle("../../data/interim/nz_cpi_group_3_clean_2023q4.pkl")

# --------------------------------------------------------------
# Transform data
# --------------------------------------------------------------

# Calculate annual percent change
cpi_data_apc=data.pct_change(periods=4) * 100

# Display top and bottom movers

index_to_filter = '2023Q4'

filtered_df = cpi_data_apc.loc[[index_to_filter]]
transposed_df=filtered_df.T
transposed_df_sorted=transposed_df.sort_values(by=index_to_filter, ascending=True).round(2)
print('Top 5 apc:')
print(transposed_df_sorted.tail(3))
print('\nBottom 5 apc:')
print(transposed_df_sorted.head(3))

# --------------------------------------------------------------
# Export data
# --------------------------------------------------------------

cpi_data_apc.to_pickle("../../data/processed/nz_cpi_group_3_apc_2023q4.pkl")
