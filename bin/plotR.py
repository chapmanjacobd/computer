#!/usr/bin/python3
from pathlib import Path
import tempfile
import argparse

from xklb.utils.processes import cmd_interactive

def start_rstudio(input_path, max_cols=3):
    plot_name = Path(input_path).stem

    r_script = f"""
    library(data.table)
    library(ggplot2)

    data <- fread('{input_path}')
    num_cols <- ncol(data)

    if (num_cols < 1) {{
        stop("The data file must have at least one column.")
    }}

    plot_data <- function(data, x_col, y_col) {{
        ggplot(data, aes(x=get(x_col), y=get(y_col))) +
          geom_point() +
          ggtitle(paste("Plot of", x_col, "vs", y_col)) +
          theme_minimal()
    }}

    if (num_cols == 1) {{
        # Plot a histogram for a single column
        ggplot(data, aes(x=V1)) +
          geom_histogram(bins=30) +
          ggtitle("Histogram of Data") +
          theme_minimal()
        ggsave("{plot_name}_plot.png")
    }} else if (num_cols <= {max_cols}) {{
        # Plot each column against the first column
        for (i in 2:num_cols) {{
            plot_data(data, "V1", paste0("V", i))
            ggsave(paste0("{plot_name}_plot_V1_V", i, ".png"))
        }}
    }} else {{
        for (i in seq(1, num_cols, {max_cols})) {{
            end_col <- min(i + {max_cols} - 1, num_cols)
            subset_data <- data[, i:end_col]
            for (j in 2:ncol(subset_data)) {{
                plot_data(subset_data, "V1", paste0("V", j))
                ggsave(paste0("{plot_name}_plot_V1_V", i + j - 1, ".png"))
            }}
        }}
    }}
    """

    with tempfile.NamedTemporaryFile('w', suffix=f"{plot_name}_plot.R") as f: # type: ignore
        f.write(r_script)
        f.flush()

        cmd_interactive("Rscript", f.name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start RStudio, load data, and plot it.")
    parser.add_argument("data_file", help="Path to the data file")
    parser.add_argument("--max_cols", type=int, default=3, help="Maximum number of columns to plot together (default: 3)")

    args = parser.parse_args()
    start_rstudio(args.data_file, args.max_cols)
