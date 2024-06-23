import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly_express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


########### Geo plot #############
# need shape file for Subnational population estimates (TA, SA2), by age and sex, at 30 June 1996-2023 (2023 boundaries)
# see https://datafinder.stats.govt.nz/layer/111194-territorial-authority-2023-generalised/


# Read the shapefile
shapefile_path = "../../data/raw/territorial-authority-2023-generalised.shp"
gdf = gpd.read_file(shapefile_path)


# Load the demographic share dataset
df = pd.read_csv("../../data/processed/pop_estimate_shares_processed.csv", sep=",")

# Filter out unneeded regions
filtered_gdf = gdf[
    ~gdf["TA2023_V_2"].isin(
        ["Area Outside Territorial Authority", "Chatham Islands Territory"]
    )
]


# Plot function
def plot_geodataframe_dark(df, gdf, year, plot_col):
    # Filter for the specified year
    df_plot = df[df["Year"] == year].copy()

    # Ensure you have consistent region names before merging with GeoDataFrame
    gdf_merged = gdf.merge(df_plot, left_on="TA2023_V_2", right_on="Region", how="left")

    # Plot the GeoDataFrame
    fig, ax = plt.subplots(figsize=(10, 10), facecolor="#282a36")
    fig.patch.set_facecolor("#282a36")  # Set the figure background color
    ax.set_facecolor("#282a36")  # Set the axes background color
    gdf_merged.plot(
        column=plot_col, ax=ax, legend=False, cmap="OrRd", edgecolor="white"
    )

    # Customize the color bar to make it smaller
    sm = plt.cm.ScalarMappable(
        cmap="OrRd",
        norm=plt.Normalize(
            vmin=gdf_merged[plot_col].min(), vmax=gdf_merged[plot_col].max()
        ),
    )
    sm._A = []
    cbar = fig.colorbar(
        sm, ax=ax, shrink=0.65
    )  # Adjust shrink to make the color bar smaller

    # Customize the color bar properties
    cbar.ax.tick_params(
        color="white", labelcolor="white"
    )  # Change the color of the ticks and labels
    cbar.outline.set_edgecolor("white")  # Change the edge color of the color bar

    # Customize the plot
    ax.set_title(
        f'{plot_col.replace("_", " ")} by Region in {year} (percent)',
        loc="left",
        fontsize=18,
        fontname="DejaVu Sans Mono",
        color="white",
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Add a source footer
    plt.annotate(
        "Source: StatisticsNZ",
        xy=(1, -0.1),
        xycoords="axes fraction",
        ha="center",
        fontsize=12,
        fontname="DejaVu Sans Mono",
        color="white",
    )

    # Save the plot as an image
    # dpi = 100  # Dots per inch
    # fig.set_size_inches(627/dpi, 1200/dpi)  # Convert pixels to inches (Optional to choose the dimensions in pixels).
    # plt.savefig('dark_choropleth_nz', dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())

    # Show the plot
    plt.show()


plot_geodataframe_dark(df, filtered_gdf, 2023, "Boomer_Share")
plot_geodataframe_dark(df, filtered_gdf, 1996, "Boomer_Share")
plot_geodataframe_dark(df, filtered_gdf, 2013, "Boomer_Share")

plot_geodataframe_dark(df, filtered_gdf, 2023, "Millennial_Share")
plot_geodataframe_dark(df, filtered_gdf, 2013, "Millennial_Share")

plot_geodataframe_dark(df, filtered_gdf, 2013, "Millennial_Boomer_Share")
plot_geodataframe_dark(df, filtered_gdf, 2023, "Millennial_Boomer_Share")


######## Small multiples plot  #########
# Millennials and Boomers are increasingly moving to the same cities. Has there been a convergence in recent years?
# Identify where Millennial and Boomer shares have increase since 2006 - use diff


# Filter the DataFrame to exclude Chatham Island and Area outside territorial authority, and include only the years 2013 and 2023
df_filtered = df[
    (df["Year"].isin([2013, 2023]))
    & (
        ~df["Region"].isin(
            ["Chatham Islands Territory", "Area Outside Territorial Authority"]
        )
    )
]

# Pivot the DataFrame to have years as columns for Millennial share, Boomer share, and Total Population
df_pivot_millennial = df_filtered.pivot(
    index="Region", columns="Year", values="Millennial_Share"
)
df_pivot_boomer = df_filtered.pivot(
    index="Region", columns="Year", values="Boomer_Share"
)
df_pivot_population = df_filtered.pivot(
    index="Region", columns="Year", values="Total_Population"
)

# Rename columns for clarity before merging
df_pivot_millennial.rename(
    columns={2023: "Millennial_2023", 2013: "Millennial_2013"}, inplace=True
)
df_pivot_boomer.rename(columns={2023: "Boomer_2023"}, inplace=True)
df_pivot_population.rename(columns={2023: "Total_Population_2023"}, inplace=True)

# Calculate the difference in Millennial share between 2013 and 2023
df_pivot_millennial["Difference"] = (
    df_pivot_millennial["Millennial_2023"] - df_pivot_millennial["Millennial_2013"]
)

# Merge the Millennial share difference with Boomer share and Total Population
df_combined = df_pivot_millennial.merge(
    df_pivot_boomer[["Boomer_2023"]], left_index=True, right_index=True
)
df_combined = df_combined.merge(
    df_pivot_population[["Total_Population_2023"]], left_index=True, right_index=True
)


# Filter regions with Boomer share greater than 25% in 2023 and total population in 2023 is greater than 10k
df_combined_filtered = df_combined[
    (df_combined["Boomer_2023"] > 21) & (df_combined["Total_Population_2023"] > 30000)
]

# Sort the DataFrame by the calculated difference in Millennial share
df_sorted_filtered_boomer = df_combined_filtered.sort_values(
    by=["Difference"], ascending=False
)

# Display the top regions with the highest increase in Millennial share
top_regions_filtered_boomer = df_sorted_filtered_boomer.head(12)

list_regions_plot = list(
    df_sorted_filtered_boomer.head(12).reset_index()["Region"].unique()
)

# Filter the DataFrame for the specified regions
multiples_df = df[df["Region"].isin(list_regions_plot)]

# Define color map for generations
color_map = {"Boomer": "blue", "Millennial": "green", "Gen X": "grey", "Gen Z": "grey"}

# Create the subplots
fig = make_subplots(
    rows=4,
    cols=3,
    shared_xaxes=True,
    shared_yaxes=True,
    subplot_titles=list_regions_plot,
)

# Plot the data
row = 1
col = 1
for region in list_regions_plot:
    region_data = multiples_df[multiples_df["Region"] == region]
    fig.add_trace(
        go.Scatter(
            x=region_data["Year"],
            y=region_data["Boomer_Share"],
            mode="lines",
            name="Boomer Share",
            legendgroup="Boomer",
            line=dict(color=color_map["Boomer"]),
            showlegend=(row == 1 and col == 1),
        ),
        row=row,
        col=col,
    )
    fig.add_trace(
        go.Scatter(
            x=region_data["Year"],
            y=region_data["Millennial_Share"],
            mode="lines",
            name="Millennial Share",
            legendgroup="Millennial",
            line=dict(color=color_map["Millennial"]),
            showlegend=(row == 1 and col == 1),
        ),
        row=row,
        col=col,
    )
    fig.add_trace(
        go.Scatter(
            x=region_data["Year"],
            y=region_data["Gen X_Share"],
            mode="lines",
            name="Gen X Share",
            legendgroup="Gen X",
            line=dict(color=color_map["Gen X"], dash="dash"),
            showlegend=(row == 1 and col == 1),
        ),
        row=row,
        col=col,
    )

    col += 1
    if col > 3:
        col = 1
        row += 1

# Update layout for dark mode and larger figure size
fig.update_layout(
    title="Population Share Over Time by Region",
    template="plotly_dark",
    plot_bgcolor="#282a36",
    paper_bgcolor="#282a36",
    showlegend=True,
    width=1400,
    height=1000,
    legend=dict(
        title="Generation",
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5,
    ),
)

# Update axes
fig.update_yaxes(title_text="")

fig.show()

###### Home ownership plot
# Load the demographic share dataset
df_ownership = pd.read_csv("../../data/raw/home_ownership_generation.csv", sep=",")


# Function to plot home ownership rates by age and generation using Plotly
def plot_ownership_by_age_and_generation_plotly(df):
    # Define the custom color palette
    colors = {
        "Gen X": "#636EFA",  # blue
        "Baby Boomer": "#B6E880",  # light green
        "Gen Z": "#FFA15A",  # orange
        "Millennial": "#EF553B",  # red
        "Silent": "#FF97FF",  # pink
    }

    # Create the plot
    fig = px.line(
        df,
        x="Age group",
        y="Home Ownership Rate",
        color="Generation",
        title="Home Ownership Rate (mean)",
        labels={
            "Age group": "Age Group",
            "Home Ownership Rate": "Home Ownership Rate (%)",
        },
        line_shape="linear",
        color_discrete_map=colors,  # Apply the custom color palette
    )

    fig.update_layout(
        xaxis_title="Age Group",
        yaxis_title="",
        legend_title_text="",
        template="plotly_dark",
        xaxis=dict(tickangle=45),
        plot_bgcolor="#282a36",
        paper_bgcolor="#282a36",
        font=dict(size=14, family="Consolas"),  # Set the font to Consolas
        title_font=dict(size=18, family="Consolas"),
    )

    fig.update_yaxes(title_text="", range=[40, 90])

    # Add footer annotation
    fig.add_annotation(
        text="Source: Statistics NZ",
        xref="paper",
        yref="paper",
        x=1.4,
        y=-0.3,
        showarrow=False,
        font=dict(size=12, color="white", family="Consolas"),
    )

    fig.show()


# Plot the data using Plotly

df_ownership_grouped = (
    df_ownership[
        (df_ownership["Generation"] != "Other")
        & (df_ownership["Generation"] != "Total")
        & (~df_ownership["Age group"].isin(["0-4", "5-9", "10-14"]))
    ]
    .groupby(["Age group", "Generation"])["Home Ownership Rate"]
    .mean()
    .reset_index()
)

plot_ownership_by_age_and_generation_plotly(df_ownership_grouped)

# Filter the data for the age ranges 25 to 74
age_ranges = [
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-74",
]
df_filtered = df_ownership[df_ownership["Age group"].isin(age_ranges)]


# Define a function to map age ranges to the new intervals
def map_age(age):
    if age in ["25-29", "30-34"]:
        return "25-34"
    elif age in ["35-39", "40-44"]:
        return "35-44"
    elif age in ["45-49", "50-54"]:
        return "45-54"
    elif age in ["55-59", "60-64"]:
        return "55-64"
    elif age in ["65-69", "70-74"]:
        return "65-74"
    else:
        return None


# Apply the function to create a new age column
df_filtered["Age_Group"] = df_filtered["Age group"].apply(map_age)

# Group the data by the new age column and calculate the mean Home Ownership Rate for each group
df_grouped = (
    df_filtered.groupby(["Year", "Age_Group"])["Home Ownership Rate"]
    .mean()
    .reset_index()
)

# Create a line plot using Plotly
fig = go.Figure()

# Define colors for each age group
colors = {
    "25-34": "#636EFA",  #  blue
    "35-44": "#B6E880",  # light green
    "45-54": "#FFA15A",  # orange
    "55-64": "#EF553B",  # red
    "65-74": "#FF97FF",  # pink
}

# Add traces for each age group
for age_group in df_grouped["Age_Group"].unique():
    age_group_data = df_grouped[df_grouped["Age_Group"] == age_group]
    fig.add_trace(
        go.Scatter(
            x=age_group_data["Year"],
            y=age_group_data["Home Ownership Rate"],
            mode="lines+markers",
            name=age_group,
            line=dict(color=colors[age_group]),
            showlegend=False,
        )
    )
    # Add annotation for the last data point of each age group
    fig.add_annotation(
        x=age_group_data["Year"].values[-1] + 1,
        y=age_group_data["Home Ownership Rate"].values[-1],
        text=age_group,
        font=dict(color=colors[age_group], family="Consolas"),
        showarrow=False,
        xanchor="left",
        yanchor="middle",
    )

# Update layout for dark mode
fig.update_layout(
    title="Home Ownership Rate (mean) by Age Group",
    template="plotly_dark",
    plot_bgcolor="#282a36",
    paper_bgcolor="#282a36",
    title_font=dict(size=18, family="Consolas"),
    xaxis_title="Year",
    yaxis_title="Home Ownership Rate",
    font=dict(size=14, family="Consolas"),
)

# Add footer annotation
fig.add_annotation(
    text="Source: Statistics NZ",
    xref="paper",
    yref="paper",
    x=1.2,
    y=-0.25,
    showarrow=False,
    font=dict(size=12, color="white", family="Consolas"),
)

fig.update_yaxes(title_text="", range=[40, 90])
fig.update_xaxes(title_text="", range=[1985, 2020])

fig.show()

############## ############## ############## ##############
# Rent inflation plot - monthly index - all locations

# Load the demographic share dataset
df_rent = pd.read_csv(
    "../../data/raw/detailed-monthly-march-2024-tla-tenancy.csv", sep=","
)


# Convert the 'Time Frame' column to datetime
df_rent["Time Frame"] = pd.to_datetime(df_rent["Time Frame"])

# Filter the DataFrame to exclude 'All', remove null location, only include 2013 and onwards
df_rent = df_rent[
    (df_rent["Location"] != "ALL")
    & (df_rent["Location"].notnull())
    & (df_rent["Time Frame"] >= ("2013-01-01"))
]

# Create df for median rent
df_median_rent = df_rent[["Time Frame", "Location", "Median Rent"]]


# Index the median rent to January 2013
def calculate_index(group):
    base = group.loc[group["Time Frame"] == "2013-01-01", "Median Rent"].mean()
    group["Index"] = group["Median Rent"] / base * 100
    return group


df_median_rent = df_median_rent.groupby("Location").apply(calculate_index)

# Get the top 12 regions with the highest increase in Millennial share
top_12_regions = [
    "Waiheke Local Board Area",
    "Central Otago District",
    "Queenstown-Lakes District",
    "Aotea/great Barrier Local Board Area",
    "Selwyn District",
    "Rodney Local Board Area",
    "Waimate District",
    "Mackenzie District",
    "Western Bay of Plenty District",
    "Waimakariri District",
    "Waitaki District",
    "Kapiti Coast District",
]

# Plot the data
fig = go.Figure()

all_regions = df_median_rent["Location"].unique()

# Plot all regions with a lighter color and low alpha
for region in all_regions:
    region_data = df_median_rent[df_median_rent["Location"] == region]
    fig.add_trace(
        go.Scatter(
            x=region_data["Time Frame"],
            y=region_data["Index"],
            mode="lines",
            name=region,
            line=dict(color="grey", width=1),
            showlegend=False,
        )
    )

# Highlight the top 12 regions
for region in top_12_regions:
    region_data = df_median_rent[df_median_rent["Location"] == region]
    fig.add_trace(
        go.Scatter(
            x=region_data["Time Frame"],
            y=region_data["Index"],
            mode="lines",
            name=region,
            line=dict(width=3),
            showlegend=True,
        )
    )

# Customize the plot
fig.update_layout(
    title="Indexed Median Rent Inflation Since January 2013",
    template="plotly_dark",
    xaxis_title="Year",
    yaxis_title="Indexed Median Rent (Jan 2013 = 100)",
    plot_bgcolor="#282a36",
    paper_bgcolor="#282a36",
    showlegend=True,
    width=1400,
    height=800,
    legend=dict(
        title="Region",
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5,
    ),
)

fig.show()

############## ############## ############## ##############
# Rent inflation plot - annual index - all locations

# Load the demographic share dataset
df_rent = pd.read_csv(
    "../../data/raw/detailed-monthly-march-2024-tla-tenancy.csv", sep=","
)

# Convert the 'Time Frame' column to datetime
df_rent["Time Frame"] = pd.to_datetime(df_rent["Time Frame"])

# Filter the DataFrame to exclude 'ALL' and remove null location
df_rent = df_rent[
    # (df_rent['Location'] != 'ALL') &
    (df_rent["Location"].notnull())
    & (df_rent["Time Frame"] >= ("2013-01-01"))
]

# Create df for median rent for all regions
df_rent["Year"] = df_rent["Time Frame"].dt.year
df_median_rent = (
    df_rent.groupby(["Location", "Year"])["Median Rent"].mean().reset_index()
)


# Index the median rent to the year 2013
def calculate_index(group):
    base = group.loc[group["Year"] == 2013, "Median Rent"].mean()
    group["Index"] = group["Median Rent"] / base * 100
    return group


df_median_rent = df_median_rent.groupby("Location").apply(calculate_index)

""" # Get the top 12 regions with the highest increase in Millennial share
top_12_regions = [
    'Waiheke Local Board Area', 'Central Otago District', 'Queenstown-Lakes District', 
    'Aotea/great Barrier Local Board Area', 'Selwyn District', 'Rodney Local Board Area', 
    'Waimate District', 'Mackenzie District', 'Western Bay of Plenty District', 
    'Waimakariri District', 'Waitaki District', 'Kapiti Coast District','ALL'
] """

""" top_12_regions = list(
    df_filtered[df_filtered['Year']==2023].sort_values(by='Boomer_Share', ascending=False).head(12).reset_index()["Region"].unique()
)+['ALL'] """

""" top_12_regions = list(
    df_filtered[df_filtered['Year']==2023].sort_values(by='Millennial_Share', ascending=False).head(20)["Region"].unique()
)+['ALL'] 

 """

""" # Regions with highest change in millenial share
top_12_regions = list(
    df_pivot_millennial.sort_values(by='Difference', ascending=False).head(20).reset_index()["Region"].unique()
)+['ALL']  """

# Regions with highest change in millenial share and boomer share high
top_12_regions = list(
    df_sorted_filtered_boomer.head(19).reset_index()["Region"].unique()
) + ["ALL"]

# Plot the data
fig = go.Figure()

all_regions = df_median_rent["Location"].unique()

# Plot all regions with a lighter color and low alpha
for region in all_regions:
    region_data = df_median_rent[df_median_rent["Location"] == region]
    fig.add_trace(
        go.Scatter(
            x=region_data["Year"],
            y=region_data["Index"],
            mode="lines",
            name=region,
            line=dict(color="grey", width=1),
            opacity=0.3,
            showlegend=False,
        )
    )

# Highlight the top 12 regions
for region in top_12_regions:
    region_data = df_median_rent[df_median_rent["Location"] == region]
    fig.add_trace(
        go.Scatter(
            x=region_data["Year"],
            y=region_data["Index"],
            mode="lines",
            name=region,
            line=dict(width=3),
            showlegend=True,
        )
    )

# Customize the plot
fig.update_layout(
    title="Indexed Median Rent Inflation Since 2013",
    template="plotly_dark",
    xaxis_title="Year",
    yaxis_title="Indexed Median Rent (2013 = 100)",
    plot_bgcolor="#282a36",
    paper_bgcolor="#282a36",
    showlegend=True,
    width=1400,
    height=800,
    legend=dict(
        title="Region",
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5,
    ),
)

fig.show()

############ Plot of population overtime ##############

# Load the dataset
df = pd.read_csv("../../data/processed/pop_estimate_processed_nz.csv", sep=",")
df_2030 = pd.read_csv("../../data/processed/pop_estimate_processed_2030.csv", sep=",")


# Concatenate df_2030 to df
df_combined = pd.concat([df, df_2030], ignore_index=True)

# Apply the relabeling function to the 'Age' column
df_combined["Age"] = df_combined["Age"].apply(
    lambda age: "90+" if age == "90 Years and over" else age
)

# Define the years of interest for plotting (excluding 2018)
years = [1996, 2006, 2023, 2030]

# Create a subplot figure with 2 rows and 2 columns
fig = make_subplots(
    rows=2, cols=2, shared_yaxes=True, subplot_titles=[f"{year}" for year in years]
)

row_col_pairs = [(1, 1), (1, 2), (2, 1), (2, 2)]

for (row, col), year in zip(row_col_pairs, years):
    # Filter data for the specific year
    year_data = df_combined[df_combined["Year"] == year]

    # Determine bar colors based on 'Generation'
    colors = [
        "orange" if gen == "Baby Boomer" else "skyblue"
        for gen in year_data["Generation"]
    ]

    # Create bar traces for each age group
    fig.add_trace(
        go.Bar(
            x=year_data["Age"],
            y=year_data["Population"],
            marker_color=colors,
            showlegend=False,
        ),
        row=row,
        col=col,
    )

# Add annotation pointing to the 'Baby Boomer' bar for 1996
fig.add_annotation(
    x="65-69 Years",
    y=250000,  # Adjust the y-coordinate to move the annotation down
    xref="x1",
    yref="y1",
    text="Baby Boomers",
    showarrow=False,
    font=dict(
        color="orange", size=16, family="Consolas"
    ),  # Increase the font size and set font family
)

# Update layout for dark mode
fig.update_layout(
    template="plotly_dark",
    width=1000,
    height=1000,
    title_text="Population Distribution by Age Group",
    plot_bgcolor="#282a36",
    paper_bgcolor="#282a36",
    font=dict(size=14, family="Consolas"),  # Set the font family for the entire plot
)

# Update axis labels and rotate x-axis tick labels
fig.update_xaxes(title_text="", tickangle=45, tickfont=dict(family="Consolas"))
fig.update_yaxes(title_text="", showticklabels=True, tickfont=dict(family="Consolas"))
fig.update_yaxes(title_text="", range=[0, 400000])

# Add footer annotation
fig.add_annotation(
    text="Source: Statistics NZ",
    xref="paper",
    yref="paper",
    x=1.05,
    y=-0.14,
    showarrow=False,
    font=dict(size=12, color="white", family="Consolas"),
)

fig.show()
