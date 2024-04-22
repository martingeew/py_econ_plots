import pandas as pd

# Load the Excel file into a DataFrame
df = pd.read_csv('population_data_nz_20240417.csv', header=[0, 1], sep=',')

# Resetting the column names to a single level by joining the multi-index levels
df.columns = [' '.join(col).strip() for col in df.columns.values]

# Melting the DataFrame to transform it from wide to long format
df_long = pd.melt(df, id_vars=['Age Year at 30 June'], var_name='Age and Year', value_name='Population')


# Extracting the year from the 'Age and Year' column
df_long['Year'] = df_long['Age and Year'].str.extract(r'(\d{4})$')

# Cleaning the 'Age' column by removing any sequence of digits that are formatted like a year
df_long['Age'] = df_long['Age and Year'].str.slice(start=0, stop=-5)

# Dropping the 'Age and Year' column as it's no longer needed
df_long.drop(columns='Age and Year', inplace=True)

df_long=df_long.rename(columns={'Age Year at 30 June':'Region'})

# save df to csv
df_long.to_csv('pop_estimate_interim.csv', index=False) 





