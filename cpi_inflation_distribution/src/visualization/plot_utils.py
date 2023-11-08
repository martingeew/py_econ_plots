import datetime
import os
import matplotlib.pyplot as plt

def save_plot_as_image(filename):
    """
    Save the current matplotlib plot as an image with the given filename.

    Parameters:
    - filename (str): The name of the file (without extension).

    Returns:
    - None
    """
    
    date = datetime.date.today().strftime("%d-%m-%Y")
    path = f"../../reports/figures/{date}/"

    # Check if the path exists, if not, create it
    if not os.path.exists(path):
        os.makedirs(path)

    plt.savefig(path + filename + ".png", bbox_inches="tight")
    print(f"Successfully exported {filename}")

# Example usage:
# ... [your plot code]
# save_plot_as_image("my_plot_name")
