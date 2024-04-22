import pandas as pd
import matplotlib.pyplot as plt

###########################################################################
# Bar plot of boomers across time

# Load the dataset
df = pd.read_csv("pop_estimate_processed_nz.csv", sep=",")

# Define the years of interest for plotting
years = [1996, 2006, 2018, 2023]

# Set up the figure for plotting 4 bar plots in a 2x2 grid
fig, axes = plt.subplots(
    nrows=2, ncols=2, figsize=(14, 10), sharey=True
)  # sharey to have uniform scale on y-axis

for i, year in enumerate(years):
    # Select subplot
    ax = axes[i // 2, i % 2]

    # Filter data for the specific year
    year_data = df[df["Year"] == year]

    # Determine bar colors based on '65 and over' condition
    colors = [
        "orange" if over_65 else "skyblue" for over_65 in year_data["65 and over"]
    ]

    # Determine hatch patterns based on 'Generation' being 'Baby Boomer'
    hatches = ["//" if gen == "Baby Boomer" else "" for gen in year_data["Generation"]]

    # Create each bar individually to apply hatches
    bars = ax.bar(year_data["Age"], year_data["Population"], color=colors)

    # Apply hatches to each bar
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    # Set titles and labels
    ax.set_title(f"Population by Age in {year}")
    ax.set_xlabel("Age")
    ax.set_ylabel("Population")

# Show the plot
plt.tight_layout()
plt.show()

###########################################################################
# waffle plot of boomers, genz, and millenials amongst population for different regions - show the extremes and largest population regions for 2023

import matplotlib.pyplot as plt
from pywaffle import Waffle
import pandas as pd

# Load the dataset
df_waffle = pd.read_csv("pop_estimate_processed_2023.csv", sep=",")

# NZ total only
df_waffle_nz = df_waffle[
    (df_waffle["Region"] == "Total, New Zealand")
    & (df_waffle["Generation"] != "Other")  # Remove under 15 year olds
].copy()

# Pivot the DataFrame using pivot_table
df_waffle_nz = df_waffle_nz.pivot_table(
    index="Generation", columns="Region", values="Population", aggfunc="sum"
)

# Waffle plot
df_plot = df_waffle_nz.copy()

# Calculate the total sum for the percentage calculation
total_population = df_plot["Total, New Zealand"].sum()

# Prepare plot details
plot = {
    # Convert actual number to a reasonable block number
    "values": [value / 100000 for value in df_plot["Total, New Zealand"].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot["Total, New Zealand"])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": "Total, New Zealand", "loc": "left", "fontsize": 12},
}

# Create the Waffle Chart
fig = plt.figure(
    FigureClass=Waffle,
    plots={311: plot},
    rows=5,  # Number of rows
    cmap_name="Accent",  # Color map name
    rounding_rule="ceil",  # Rounding rule for values
    figsize=(8, 6),  # Figure size
)

# Display the chart
plt.show()

# NZ + other regions waffle plot
region_1 = "Thames-Coromandel district"
region_2 = "Queenstown-Lakes district"
region_3 = "Waitemata local board area"
scale_factor = 1000

df_waffle_region = df_waffle[
    (df_waffle["Region"].isin([region_1, region_2, region_3]))
    & (df_waffle["Generation"] != "Other")  # Remove under 15 year olds
].copy()

# Pivot the DataFrame using pivot_table
df_waffle_region = df_waffle_region.pivot_table(
    index="Generation", columns="Region", values="Population", aggfunc="sum"
)

df_plot = df_waffle_region.copy()

# Calculate the total sum for the percentage calculation
total_population = df_plot[region_1].sum()

plot1 = {
    # Convert actual number to a reasonable block number
    "values": [value / scale_factor for value in df_plot[region_1].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot[region_1])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": region_1, "loc": "left", "fontsize": 12},
}

total_population = df_plot[region_2].sum()

plot2 = {
    # Convert actual number to a reasonable block number
    "values": [value / scale_factor for value in df_plot[region_2].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot[region_2])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": region_2, "loc": "left", "fontsize": 12},
}

total_population = df_plot[region_3].sum()

plot3 = {
    # Convert actual number to a reasonable block number
    "values": [value / scale_factor for value in df_plot[region_3].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot[region_3])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": region_3, "loc": "left", "fontsize": 12},
}

fig = plt.figure(
    FigureClass=Waffle,
    plots={
        311: plot1,
        312: plot2,
        313: plot3,
    },
    rows=5,  # Outside parameter applied to all subplots, same as below
    cmap_name="Accent",  # Change color with cmap
    rounding_rule="ceil",  # Change rounding rule, so value less than 1000 will still have at least 1 block
    figsize=(8, 6),
)

# Add a title and a small detail at the bottom
fig.suptitle("Population demographics by region", fontsize=14, fontweight="bold")
fig.supxlabel(
    "1 block = 1k people",
    fontsize=8,
    x=0.14,  # position at the 14% axis
)
fig.set_facecolor("#EEEDE7")

plt.show()

# NZ + main centres waffle plot
region_1 = "Wellington city"
region_2 = "Auckland"
region_3 = "Christchurch city"
scale_factor = 10000

df_waffle_region = df_waffle[
    (df_waffle["Region"].isin([region_1, region_2, region_3]))
    & (df_waffle["Generation"] != "Other")  # Remove under 15 year olds
].copy()

# Pivot the DataFrame using pivot_table
df_waffle_region = df_waffle_region.pivot_table(
    index="Generation", columns="Region", values="Population", aggfunc="sum"
)

df_plot = df_waffle_region.copy()

# Calculate the total sum for the percentage calculation
total_population = df_plot[region_1].sum()

plot1 = {
    # Convert actual number to a reasonable block number
    "values": [value / scale_factor for value in df_plot[region_1].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot[region_1])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": region_1, "loc": "left", "fontsize": 12},
}

total_population = df_plot[region_2].sum()

plot2 = {
    # Convert actual number to a reasonable block number
    "values": [value / scale_factor for value in df_plot[region_2].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot[region_2])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": region_2, "loc": "left", "fontsize": 12},
}

total_population = df_plot[region_3].sum()

plot3 = {
    # Convert actual number to a reasonable block number
    "values": [value / scale_factor for value in df_plot[region_3].tolist()],
    # Change labels to display the percentage of the whole
    "labels": [
        f"{index} ({value/total_population:.1%})"
        for index, value in zip(df_plot.index, df_plot[region_3])
    ],
    "legend": {"loc": "upper left", "bbox_to_anchor": (1.05, 1), "fontsize": 8},
    "title": {"label": region_3, "loc": "left", "fontsize": 12},
}

fig = plt.figure(
    FigureClass=Waffle,
    plots={
        311: plot1,
        312: plot2,
        313: plot3,
    },
    rows=5,  # Outside parameter applied to all subplots, same as below
    cmap_name="Accent",  # Change color with cmap
    rounding_rule="ceil",  # Change rounding rule, so value less than 1000 will still have at least 1 block
    figsize=(8, 6),
)

# Add a title and a small detail at the bottom
fig.suptitle("Population demographics by region", fontsize=14, fontweight="bold")
fig.supxlabel(
    "1 block = 10k people",
    fontsize=8,
    x=0.14,  # position at the 14% axis
)
fig.set_facecolor("#EEEDE7")

plt.show()

###########################################################################
# Waffle function with Icon

# colorblind_palette = sns.color_palette("colorblind").as_hex()
# pastel_palette = sns.color_palette("colorblind").as_hex()
# print(colorblind_palette)
# cmap accent =['#7fc97f', '#beaed4', '#fdc086', '#bf5b17', '#386cb0']
# pastel = ['#0173b2', '#de8f05', '#029e73', '#d55e00', '#ece133']

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # for the legend
from pywaffle import Waffle
import pandas as pd

# NZ + other regions waffle plot
region_1 = "Thames-Coromandel district"
region_2 = "Queenstown-Lakes district"
region_3 = "Waitemata local board area"
scale_factor = 1000

df_waffle_region = df_waffle[
    (df_waffle["Region"].isin([region_1, region_2, region_3]))
    & (df_waffle["Generation"] != "Other")  # Remove under 15 year olds
].copy()

# Pivot the DataFrame using pivot_table
df_waffle_region = df_waffle_region.pivot_table(
    index="Generation", columns="Region", values="Population", aggfunc="sum"
)


df_plot = df_waffle_region.copy()


number_of_bars = len(df_plot.columns)  # one bar per year


BLUE = "#0173b2"
RED = "#de8f05"
GREEN = "#029e73"
YELLOW = "#ece133"
PINK='#cc78bc'
colors = [BLUE, RED, GREEN, YELLOW, PINK]
#colors=['#4a7493', '#b6a57a', '#5a7d6d', '#a3735a', '#b3b179']

# Init the whole figure and axes
fig, axs = plt.subplots(
    nrows=1,
    ncols=3,
    figsize=(10, 6),
)

# Iterate over each bar and create it
for i, ax in enumerate(axs):

    col_name = df_plot.columns[i]
    values = df_plot[col_name] / 1000  # values from the i-th column
    # values = df_plot[col_name]   # values from the i-th column

    Waffle.make_waffle(
        ax=ax,  # pass axis to make_waffle
        rows=20,
        columns=5,
        values=values,
        title={"label": col_name, "loc": "left"},
        colors=colors,
        vertical=True,
        #icons='person',
        #font_size=0.01,  # size of each point
        #icon_legend=True,
        legend={"loc": "upper left", "bbox_to_anchor": (1, 1)},
    )

# Add a title
fig.suptitle(
    "Population Demographics by Region", fontsize=14, fontweight="bold",ha='right'
)


# Add a legend
legend_labels = df_plot.index
legend_elements = [
    mpatches.Patch(color=colors[i], label=legend_labels[i]) for i in range(len(colors))
]
fig.legend(
    handles=legend_elements,
    loc="upper right",
    title="Generation",
    bbox_to_anchor=(1.04, 0.9),
)

plt.subplots_adjust(right=0.85, wspace=0.5)
plt.show()

###########################################################################
# Heat map of generation vs region with proportion as values

import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df_heatmap = pd.read_csv("pop_estimate_processed_2023.csv", sep=",")

# Pivot the DataFrame using pivot_table
df_heatmap_pivot = df_heatmap.pivot_table(
    index="Region", columns="Generation", values="Population", aggfunc="sum"
)

# Calculate the total population per region (sum across columns)
region_totals = df_heatmap_pivot.sum(axis=1)

# Divide each value in the dataframe by the corresponding region total to get the population share
df_heatmap_pivot_share = df_heatmap_pivot.div(region_totals, axis=0)

# Create the heatmap
plt.figure(figsize=(14, 20))
sns.heatmap(df_heatmap_pivot_share, annot=True, fmt=".2%", cmap="coolwarm")
plt.title("Population Share by Generation and Region")
plt.xlabel("Generation")
plt.ylabel("Region")
plt.show()

###########################################################################
# Plot a horizontal bar plot of boomer share by TA
# a scatter plot or Millenial vs Boomer

# Geomap of specific regions like Auckland, Wellington, Christchurch, Hamilton

# how will the competition for houses change in different regions?
