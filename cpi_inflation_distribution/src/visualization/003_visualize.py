import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from plot_utils import save_plot_as_image

cpi_data_apc = pd.read_pickle("../../data/processed/nz_cpi_group_3_apc.pkl")

# --------------------------------------------------------------
# Set styling
# --------------------------------------------------------------

# Colour pallete
GREY10 = "#1a1a1a"
GREY30 = "#4d4d4d"
GREY40 = "#666666"
GREY50 = "#7f7f7f"
GREY60 = "#999999"
GREY75 = "#bfbfbf"
GREY91 = "#e8e8e8"
GREY98 = "#fafafa"
CHARCOAL = "#333333"

# colorblind_palette = sns.color_palette("colorblind").as_hex()
BLUE = "#0173b2"
RED = "#de8f05"
GREEN = "#029e73"

# Set font family
font_family = "Consolas"  # techy feel
plt.rcParams["font.family"] = font_family

# Set global spine customizations
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.left"] = False
plt.rcParams["axes.spines.bottom"] = True

# Set tick color for the x-axis
plt.rcParams["xtick.color"] = GREY40
# plt.rcParams['ytick.color'] = GREY40
plt.rcParams["ytick.left"] = False

# Choose grid options
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.grid.axis"] = "y"
plt.rcParams["grid.color"] = GREY91
plt.rcParams["grid.linewidth"] = 1.0

# Set global tick label font size
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12

# --------------------------------------------------------------
# Create plot
# --------------------------------------------------------------


def plot_multiple_densities_seaborn(df, index_rows, percentile_range=None):
    """
    Plot density curves of the CPI annual percentage change for specified index rows using seaborn.
    Optionally exclude data points outside the top and bottom percentiles.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the CPI data.
    index_rows (list): A list of index labels for the rows for which to plot the density curves.
    percentile_range (float, optional): If provided, exclude data points outside the top and bottom percentiles.
    """

    # Set up the matplotlib figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))

    custom_palette = [BLUE, GREEN, RED]

    for index_row, color in zip(index_rows, custom_palette):
        # Select the row for the specified index
        row_data = df.loc[index_row]

        # Exclude outliers if percentile_range is provided
        if percentile_range is not None:
            lower_percentile = np.percentile(row_data, percentile_range)
            upper_percentile = np.percentile(row_data, 100 - percentile_range)
            row_data = row_data[
                (row_data >= lower_percentile) & (row_data <= upper_percentile)
            ]

        # Plot a density curve with seaborn on the specified axes
        sns.kdeplot(
            row_data,
            bw_adjust=0.5,
            label=index_row,
            ax=ax,
            fill=True,
            alpha=0.1,
            linewidth=2,
            color=color,
        )

    # Adding a horizontal line at y=0
    ax.axvline(0, color=GREY40, linestyle="--", alpha=0.75)

    # Adding legend
    # ax.legend(title=None)

    # Adding labels
    ax.set_xlabel("Annual Percent Change")
    ax.set_ylabel("Density")

    return fig, ax


fig, ax = plot_multiple_densities_seaborn(
    cpi_data_apc, ["2023Q3", "2022Q3", "2020Q3"], percentile_range=2
)

# --------------------------------------------------------------
# Plot specific customizations
# --------------------------------------------------------------

# Customize the start, end, and frequency of the x tick labels
x_start = -15.0
x_end = 20.0
x_frequency = 5
x_ticks = np.arange(x_start, x_end + x_frequency, x_frequency)
x_ticks = np.round(x_ticks).astype(int)

ax.set_xticks(x_ticks)
ax.set_xticklabels(x_ticks, weight=500, color=GREY40)

# Customize the start, end, and frequency of the y tick labels
current_ticks = ax.get_yticks()
new_ticks = np.arange(current_ticks.min(), current_ticks.max() + 0.05, 0.05)
ax.set_yticks(new_ticks)
new_ticks = np.round(new_ticks,2)
ax.set_yticklabels(new_ticks, weight=500, color=GREY40)

# customize legend
# ax.legend(title=None, fontsize="12")

# Customize x labels
ax.set_xlabel("Annual percent change", fontsize=14, labelpad=15)

# Set y labels size and padding
ax.set_ylabel("Density", fontsize=14, labelpad=15)

# Customize y labels
colors = [BLUE, GREEN, RED]  # List of colors for each curve
points = [
    (8, 0.09),
    (15, 0.018),
    (-2.5, 0.055),
]  # List of points to annotate (x, y) on the density curves
texts = ["2023-Q3", "2022-Q3", "2020-Q3"]  # List of annotation texts
connectionstyles = [
    "arc3,rad=-0.3",
    "arc3,rad=-0.3",
    "arc3,rad=0.2",
]  # Different connection styles for each annotation

for point, text, color, conn_style in zip(points, texts, colors, connectionstyles):
    ax.annotate(
        text,
        xy=point,
        xytext=(point[0] - 0.1, point[1] + 0.05),
        arrowprops=dict(
            facecolor=color, # Set the color of the arrowhead (the "face" of the arrow) 
            shrink=0.01,# Shrink the start and end of the arrow by a small fraction to avoid overlap with the text and point
            headwidth=8,  # Set the width of the arrowhead
            width=0.6,  # Set the width of the arrow's body (the line part)
            connectionstyle=conn_style,
            alpha=0.5,
        ),
        fontsize=12,
        color=color,
        ha="center",
    )

# Add title
fig.suptitle(
    "CPI Inflation Density Distribution in New Zealand",
    fontsize=22,
    x=0.05,
    y=0.97,
    ha="left",
    color=CHARCOAL,
    weight="bold",
)

# Add subtitle
ax.set_title(
    "'Smoothed histogram' of annual inflation across CPI level 2 subgroups",
    loc="left",
    fontsize=16,
    x=-0.06,
    # y=1.2,
    pad=25,  # padding between the top of the plot and the subheading
    color=CHARCOAL,
)

# Add annotations
ax.annotate(
    "@mardywong",
    xy=(1.0, -0.25),
    xycoords="axes fraction",
    ha="right",
    va="center",
    fontsize=11,
    color=CHARCOAL,
)

ax.annotate(
    "Source: Statistics NZ",
    xy=(-0.07, -0.25),
    xycoords="axes fraction",
    ha="left",
    va="center",
    fontsize=11,
    color=CHARCOAL,
)

plt.tight_layout()
save_plot_as_image(filename="cpi_inflation_density_nz")  # Save the image into a folder
plt.show()
