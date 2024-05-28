import pandas as pd

df = pd.read_csv("../../data/interim/pop_estimate_interim.csv", sep=",")

df = df[df["Age"] != "Total people, age"]

# Replace the specific string in the 'region' column
df["Region"] = df["Region"].replace(
    "Total, New Zealand by territorial authority/SA2", "Total, New Zealand"
)


def determine_generation(census_year, age_description):
    """
    Determines the generation category based on birth year calculated from the census year and age description.

    Parameters:
        census_year (int): The year of the census.
        age_description (str): Description of the age group, could be a range, a specific age, or an 'over' format.

    Returns:
        str: The generation name.
    """
    # Check for numeric age or age range in the description
    if "-" in age_description:
        # It's a range, get the lower bound as the oldest possible age
        oldest_age = int(age_description.split("-")[0])
    elif "over" in age_description:
        # It's an 'over' description, extract the number
        oldest_age = int(age_description.split(" ")[0])
    else:
        # Otherwise, assume the entire string is a numeric age
        oldest_age = int(age_description)

    # Calculate the birth year assuming the age is the oldest age in the range
    birth_year = census_year - oldest_age

    # Determine generation based on birth year
    if 1946 <= birth_year <= 1964:
        return "Baby Boomer"
    elif 1965 <= birth_year <= 1980:
        return "Gen X"
    elif 1981 <= birth_year <= 1996:
        return "Millennial"
    elif 1928 <= birth_year <= 1945:
        return "Silent"
    elif 1997 <= birth_year <= 2012:
        return "Gen Z"
    else:
        return "Other"  # Return an empty string for ages outside these ranges


# Apply the function to each row to categorize generations
df["Generation"] = df.apply(
    lambda row: determine_generation(row["Year"], row["Age"]), axis=1
)


# Add a column that marks if the Age group is 65 years and over
old_age_groups = [
    "65-69 Years",
    "70-74 Years",
    "75-79 Years",
    "80-84 Years",
    "85-89 Years",
    "90 Years and over",
]
df["65 and over"] = df["Age"].isin(old_age_groups)


def age_to_numeric(age):
    """
    Converts age range strings to a numeric value by extracting the first age in the range.
    Handles special cases like '90 Years and over' by stripping non-numeric characters and returning the integer.

    Parameters:
        age (str): The age range as a string.

    Returns:
        int: The numeric value representing the lower bound of the age range.
    """
    # Handle the special case where the format is different (e.g., '90 Years and over')
    if "over" in age:
        # Extract numbers only and convert to integer
        return int("".join(filter(str.isdigit, age)))
    # Standard case: extract the first part of the age group string and convert to integer
    return int(age.split("-")[0])


# Use the function as a key for sorting
df["Age"] = df["Age"].astype(str)  # Ensure the Age column is of type string
df = df.sort_values("Age", key=lambda x: x.map(age_to_numeric))


# save df for NZ only to csv
df_nz = df[(df["Region"] == "Total, New Zealand")].copy()
df_nz.to_csv("../../data/processed/pop_estimate_processed_nz.csv", index=False)

# save df for All regions but 2023 only
df_2023 = df[(df["Year"] == 2023)].copy()
df_2023.to_csv("../../data/processed/pop_estimate_processed_2023.csv", index=False)

# save complete data
df.to_csv("../../data/processed/pop_estimate_processed.csv", index=False)


###### Data by selected populatino share #######
# Filter the DataFrame for Boomers and Millennials
filtered_df = df[df["Generation"].isin(["Baby Boomer", "Millennial", "Gen Z", "Gen X"])]

# Calculate the total population for each region and year
total_population_df = df.groupby(["Region", "Year"])["Population"].sum().reset_index()
total_population_df.rename(columns={"Population": "Total_Population"}, inplace=True)

#  Merge the total population with the filtered DataFrame
merged_df = pd.merge(filtered_df, total_population_df, on=["Region", "Year"])

# Pivot the DataFrame to compare Population for Boomers and Millennials
comparison_df = merged_df.pivot_table(
    index=["Region", "Year", "Total_Population"],
    columns="Generation",
    values="Population",
    aggfunc="sum",
).reset_index()

# Rename columns for clarity
comparison_df.columns.name = None
comparison_df.rename(
    columns={
        "Baby Boomer": "Boomer_Population",
        "Millennial": "Millennial_Population",
        "Gen Z": "Gen Z_Population",
        "Gen X": "Gen X_Population",
    },
    inplace=True,
)

# Calculate population shares
comparison_df["Boomer_Share"] = (
    comparison_df["Boomer_Population"] / comparison_df["Total_Population"]
)
comparison_df["Millennial_Share"] = (
    comparison_df["Millennial_Population"] / comparison_df["Total_Population"]
)
comparison_df["Gen Z_Share"] = (
    comparison_df["Gen Z_Population"] / comparison_df["Total_Population"]
)
comparison_df["Gen X_Share"] = (
    comparison_df["Gen X_Population"] / comparison_df["Total_Population"]
)
comparison_df["Millennial_Boomer_Share"] = (
    comparison_df["Millennial_Share"] + comparison_df["Boomer_Share"]
)

# save data
comparison_df.to_csv(
    "../../data/processed/pop_estimate_shares_processed.csv", index=False
)
