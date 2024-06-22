import pandas as pd

############### Population estimates by TA2 #####################

# Load the Excel file into a DataFrame
df = pd.read_csv('../../data/raw/population_data_nz_20240417.csv', header=[0, 1], sep=',')

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
df_long.to_csv('../../data/interim/pop_estimate_interim.csv', index=False) 

############### Population projections by TA2 #####################
import pandas as pd

# Load the Excel file into a DataFrame
df = pd.read_csv('../../data/raw/pop_projections_TA2.csv', header=[0, 1], sep=',')

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

df_long.to_csv('../../data/interim/pop_projection_interim.csv', index=False) 

############### Population projections by age for 2030 #####################

df_proj_2030=pd.read_csv("../../data/raw/pop_projection_age_2030.csv", sep=",")
# Pivot to match format above

############### Population projections national #####################

df_proj=pd.read_csv("../../data/raw/pop_projection_national.csv", sep=",")
# make scenario cols as cols


