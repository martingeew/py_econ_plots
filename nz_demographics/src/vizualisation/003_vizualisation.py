import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

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
def plot_geodataframe(df, gdf, year, plot_col):
    # Filter for the specified year
    df_plot = df[df['Year'] == year].copy()

    # Ensure you have consistent region names before merging with GeoDataFrame
    gdf_merged = gdf.merge(df_plot, left_on='TA2023_V_2', right_on='Region', how='left')

    # Plot the GeoDataFrame
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_merged.plot(column=plot_col, ax=ax, legend=False, cmap='OrRd', edgecolor='black')

    # Customize the color bar to make it smaller
    sm = plt.cm.ScalarMappable(cmap='OrRd', norm=plt.Normalize(vmin=gdf_merged[plot_col].min(), vmax=gdf_merged[plot_col].max()))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, shrink=0.65)  # Adjust shrink to make the color bar smaller

    # Customize the plot
    ax.set_title(f'Share of {plot_col.replace("_", " ")} by Region (percent)', loc='left', fontsize=18)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Show the plot
    plt.show()
    
plot_geodataframe(df, filtered_gdf, 2023, 'Boomer_Share')
plot_geodataframe(df, filtered_gdf, 1996, 'Boomer_Share')
plot_geodataframe(df, filtered_gdf, 2013, 'Boomer_Share')

plot_geodataframe(df, filtered_gdf, 2013, 'Millennial_Boomer_Share')
plot_geodataframe(df, filtered_gdf, 2023, 'Millennial_Boomer_Share')

########### Interactive Geo plot #############
import json

def plot_geodataframe_interactive(df, gdf, year, plot_col):
    # Filter for the specified year
    df_plot = df[df['Year'] == year].copy()

    # Ensure you have consistent region names before merging with GeoDataFrame
    gdf_merged = gdf.merge(df_plot, left_on='TA2023_V_2', right_on='Region', how='left')

    # Convert the GeoDataFrame to GeoJSON format
    geojson = gdf_merged.to_json()

    # Create an interactive choropleth map
    fig = px.choropleth(
        gdf_merged,
        geojson=geojson,
        locations='TA2023_V_2',
        featureidkey='properties.TA2023_V_2',
        color=plot_col,
        hover_name='Region',
        hover_data={plot_col: True},
        color_continuous_scale="OrRd"
    )

    # Update the layout for the title and remove axis labels
    fig.update_layout(
        title_text=f'Share of {plot_col.replace("_", " ")} by Region (percent)',
        title_x=0.5,
        title_font_size=18,
        geo=dict(
            showframe=False,
            showcoastlines=False,
        )
    )

    fig.show()


plot_geodataframe_interactive(df, filtered_gdf, 2023, 'Boomer_Share')

# Filter for the specified year
df_plot = df[df['Year'] == 2023].copy()

# Ensure you have consistent region names before merging with GeoDataFrame
gdf_merged = filtered_gdf.merge(df_plot, left_on='TA2023_V_2', right_on='Region', how='left')

# Convert the GeoDataFrame to GeoJSON format
geojson = gdf_merged.to_json()


############ Multiples plot ################
# Filter for the specified year
df_plot = df[df['Year'] == 2023].copy()

# Ensure you have consistent region names before merging with GeoDataFrame
gdf_merged = filtered_gdf.merge(df_plot, left_on='TA2023_V_2', right_on='Region', how='left')

# Get the first 16 regions
first_16_regions = list(gdf_merged[
 (gdf_merged["Millennial_Boomer_Share"] > 0.42)
].sort_values(by='Millennial_Boomer_Share',ascending=False)["Region"].unique()[:16])

# Filter the DataFrame for the specified regions
multiples_df = df[df["Region"].isin(first_16_regions)]

# Create the small multiples plot
# Could show the other generations in grey in background (Gen X and Gen Z)
fig, axes = plt.subplots(4, 4, figsize=(20, 15), sharex=True, sharey=True)
axes = axes.flatten()

for i, region in enumerate(first_16_regions):
    ax = axes[i]
    region_data = multiples_df[multiples_df["Region"] == region]
    sns.lineplot(
        x="Year", y="Boomer_Share", data=region_data, ax=ax, label="Boomer Share"
    )
    sns.lineplot(
        x="Year",
        y="Millennial_Share",
        data=region_data,
        ax=ax,
        label="Millennial Share",
    )
    ax.set_title(region)
    ax.set_xlabel("")
    ax.set_ylabel("Population Share")

# Adjust the layout and display the plot
plt.tight_layout()
plt.show()

######## Small multiples plot based on correlation #########
# Millennials and Boomers are increasingly moving to the same cities. Has there been a convergence in recent years?
# Identify where Millennial and Boomer shares have increase since 2013