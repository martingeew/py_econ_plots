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


######## Small multiples plot based on correlation #########
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

# Pivot the DataFrame to have years as columns for Millennial share and Boomer share
df_pivot_millennial = df_filtered.pivot(
    index="Region", columns="Year", values="Millennial_Share"
)
df_pivot_boomer = df_filtered.pivot(
    index="Region", columns="Year", values="Boomer_Share"
)

# Rename columns for clarity before merging
df_pivot_millennial.rename(
    columns={2023: "Millennial_2023", 2013: "Millennial_2013"}, inplace=True
)
df_pivot_boomer.rename(columns={2023: "Boomer_2023"}, inplace=True)

# Calculate the difference in Millennial share between 2013 and 2023
df_pivot_millennial["Difference"] = (
    df_pivot_millennial["Millennial_2023"] - df_pivot_millennial["Millennial_2013"]
)

# Merge the Millennial share difference with Boomer share
df_combined = df_pivot_millennial.merge(
    df_pivot_boomer[["Boomer_2023"]], left_index=True, right_index=True
)

# Filter regions with Boomer share greater than 25% in 2023
df_filtered_boomer = df_combined[df_combined["Boomer_2023"] > 25]

# Sort the DataFrame by the calculated difference in Millennial share
df_sorted_filtered_boomer = df_filtered_boomer.sort_values(
    by="Difference", ascending=False
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
    fig = px.line(
        df,
        x="Age group",
        y="Home Ownership Rate",
        color="Generation",
        title="Home Ownership Rate by Age and Generation",
        labels={
            "Age group": "Age Group",
            "Home Ownership Rate": "Home Ownership Rate (%)",
        },
        line_shape="linear",
    )

    fig.update_layout(
        xaxis_title="Age Group",
        yaxis_title="",
        legend_title_text="Generation",
        template="plotly_dark",
        xaxis=dict(tickangle=45),
        plot_bgcolor="#282a36",
        paper_bgcolor="#282a36",
    )

    fig.show()


# Plot the data using Plotly
plot_ownership_by_age_and_generation_plotly(
    df_ownership[
        (df_ownership["Generation"] != "Other")
        & (df_ownership["Generation"] != "Total")
        & (~df_ownership["Age group"].isin(["0-4", "5-9", "10-14"]))
    ]
)

############## ############## ############## ############## 
# Rent inflation plot - monthly index - all locations

# Load the demographic share dataset
df_rent = pd.read_csv(
    "../../data/raw/detailed-monthly-march-2024-tla-tenancy.csv", sep=","
)


# Convert the 'Time Frame' column to datetime
df_rent['Time Frame'] = pd.to_datetime(df_rent['Time Frame'])

# Filter the DataFrame to exclude 'All', remove null location, only include 2013 and onwards
df_rent = df_rent[
    (df_rent['Location']!= 'ALL')
    &(df_rent['Location'].notnull())
    &(df_rent['Time Frame']>=('2013-01-01'))
]

# Create df for median rent
df_median_rent = df_rent[[
    'Time Frame',
    'Location',
    'Median Rent'
]]

# Index the median rent to January 2013
def calculate_index(group):
    base = group.loc[group['Time Frame'] == '2013-01-01', 'Median Rent'].mean()
    group['Index'] = group['Median Rent'] / base * 100
    return group

df_median_rent = df_median_rent.groupby('Location').apply(calculate_index)

# Get the top 12 regions with the highest increase in Millennial share
top_12_regions = [
    'Waiheke Local Board Area', 'Central Otago District', 'Queenstown-Lakes District', 
    'Aotea/great Barrier Local Board Area', 'Selwyn District', 'Rodney Local Board Area', 
    'Waimate District', 'Mackenzie District', 'Western Bay of Plenty District', 
    'Waimakariri District', 'Waitaki District', 'Kapiti Coast District'
]

# Plot the data
fig = go.Figure()

all_regions = df_median_rent['Location'].unique()

# Plot all regions with a lighter color and low alpha
for region in all_regions:
    region_data = df_median_rent[df_median_rent['Location'] == region]
    fig.add_trace(go.Scatter(x=region_data["Time Frame"], y=region_data["Index"], mode='lines', name=region, line=dict(color='grey', width=1), showlegend=False))

# Highlight the top 12 regions
for region in top_12_regions:
    region_data = df_median_rent[df_median_rent['Location'] == region]
    fig.add_trace(go.Scatter(x=region_data["Time Frame"], y=region_data["Index"], mode='lines', name=region, line=dict(width=3), showlegend=True))

# Customize the plot
fig.update_layout(
    title='Indexed Median Rent Inflation Since January 2013',
    template='plotly_dark',
    xaxis_title='Year',
    yaxis_title='Indexed Median Rent (Jan 2013 = 100)',
    plot_bgcolor='#282a36',
    paper_bgcolor='#282a36',
    showlegend=True,
    width=1400,
    height=800,
    legend=dict(
        title="Region",
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    )
)

fig.show()

############## ############## ############## ############## 
# Rent inflation plot - annual index - all locations

# Load the demographic share dataset
df_rent = pd.read_csv(
    "../../data/raw/detailed-monthly-march-2024-tla-tenancy.csv", sep=","
)

# Convert the 'Time Frame' column to datetime
df_rent['Time Frame'] = pd.to_datetime(df_rent['Time Frame'])

# Filter the DataFrame to exclude 'ALL' and remove null location
df_rent = df_rent[
    # (df_rent['Location'] != 'ALL') &
    (df_rent['Location'].notnull())
    &(df_rent['Time Frame']>=('2013-01-01'))
]

# Create df for median rent for all regions
df_rent['Year'] = df_rent['Time Frame'].dt.year
df_median_rent = df_rent.groupby(['Location', 'Year'])['Median Rent'].mean().reset_index()

# Index the median rent to the year 2013
def calculate_index(group):
    base = group.loc[group['Year'] == 2013, 'Median Rent'].mean()
    group['Index'] = group['Median Rent'] / base * 100
    return group

df_median_rent = df_median_rent.groupby('Location').apply(calculate_index)

# Get the top 12 regions with the highest increase in Millennial share
top_12_regions = [
    'Waiheke Local Board Area', 'Central Otago District', 'Queenstown-Lakes District', 
    'Aotea/great Barrier Local Board Area', 'Selwyn District', 'Rodney Local Board Area', 
    'Waimate District', 'Mackenzie District', 'Western Bay of Plenty District', 
    'Waimakariri District', 'Waitaki District', 'Kapiti Coast District','ALL'
]

# Plot the data
fig = go.Figure()

all_regions = df_median_rent['Location'].unique()

# Plot all regions with a lighter color and low alpha
for region in all_regions:
    region_data = df_median_rent[df_median_rent['Location'] == region]
    fig.add_trace(go.Scatter(x=region_data["Year"], y=region_data["Index"], mode='lines', name=region, line=dict(color='grey', width=1),opacity=0.3, showlegend=False))

# Highlight the top 12 regions
for region in top_12_regions:
    region_data = df_median_rent[df_median_rent['Location'] == region]
    fig.add_trace(go.Scatter(x=region_data["Year"], y=region_data["Index"], mode='lines', name=region, line=dict(width=3), showlegend=True))

# Customize the plot
fig.update_layout(
    title='Indexed Median Rent Inflation Since 2013',
    template='plotly_dark',
    xaxis_title='Year',
    yaxis_title='Indexed Median Rent (2013 = 100)',
    plot_bgcolor='#282a36',
    paper_bgcolor='#282a36',
    showlegend=True,
    width=1400,
    height=800,
    legend=dict(
        title="Region",
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    )
)

fig.show()