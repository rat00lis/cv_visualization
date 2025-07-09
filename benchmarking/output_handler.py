import json

def load_results(file_path):
    """
    Load results from a JSON file.
    
    :param file_path: Path to the JSON file containing results.
    :return: Parsed JSON data as a dictionary.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    return data.get("result", {})

def parse_results(results):
    """
    Parse results to extract relevant information.
    
    :param results: Dictionary containing results data.
    :return: List of dictionaries with parsed results.
    """
    parsed_results = []
    measurement_unit = None

    for key, value in results.items():
        measurement_unit = value.get("measurement_unit", "unknown")
        parsed_result = {
            "option": value.get("option", "unknown"),
            "min": value.get("min", 0.0),
            "mean": value.get("mean", 0.0),
            "max": value.get("max", 0.0),
            "stdev": value.get("stdev", 0.0),
            "n_size": value.get("n_size", 0),
            "n_out": value.get("n_out", 0)
        }
        parsed_results.append(parsed_result)
    
    return parsed_results, measurement_unit

def create_ordered_results(parsed_results):
    """
    Create ordered results based on the 'n_size' and 'option'.
    
    :param parsed_results: List of parsed results.
    :return: Ordered dictionary with results.
    """
    ordered_results = {}
    
    for result in parsed_results:
        n_size = result["n_size"]
        option = result["option"]
        
        if n_size not in ordered_results:
            ordered_results[n_size] = {}
        
        ordered_results[n_size][option] = result
    
    return ordered_results

def create_plot_from_results(ordered_results, 
                            measurement_unit, 
                            title="Benchmarking Results",
                            x_label="N Size",
                            y_label="Time (seconds)",
                            add_error_bars=False,
                            error_bar_type="stdev",
                            add_legend=True,
                            add_grid=True,
                            use_log=False,
                            smooth_plot=False,
                            output_path="benchmarking_results_plot.png"
                            ):
    
    # create data frame
    import pandas as pd
    rows = []
    for n_size in ordered_results:
        for option, result in ordered_results[n_size].items():
            row = {
                "n_size": n_size,
                "option": option,
                "mean": result["mean"],
                "stdev": result["stdev"],
                "min": result["min"],
                "max": result["max"]
            }
            rows.append(row)
    
    dataframe = pd.DataFrame(rows)
    dataframe = dataframe.sort_values(by=["n_size", "option"])
    dataframe.set_index("n_size", inplace=True)
    dataframe = dataframe.pivot(columns="option", values="mean")
    dataframe = dataframe.fillna(0) 
    dataframe = dataframe.astype(float)
    # create plot
    import matplotlib.pyplot as plt
    from scipy.interpolate import make_interp_spline
    import numpy as np
    
    plt.figure(figsize=(10, 6))
    for option in dataframe.columns:
        if smooth_plot and len(dataframe.index) > 3:
            # Create smooth curve
            x = np.array(dataframe.index)
            y = np.array(dataframe[option])
            x_smooth = np.linspace(min(x), max(x), 300)
            spline = make_interp_spline(x, y, k=3)
            y_smooth = spline(x_smooth)
            plt.plot(x_smooth, y_smooth, label=option)
        else:
            plt.plot(dataframe.index, dataframe[option], label=option)
            
        if add_error_bars:
            if error_bar_type == "stdev":
                plt.errorbar(dataframe.index, dataframe[option], yerr=dataframe["stdev"], fmt='o', capsize=5)
            elif error_bar_type == "min_max":
                plt.fill_between(dataframe.index, dataframe["min"], dataframe["max"], alpha=0.2)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(f"{y_label} ({measurement_unit})")
    if use_log:
        plt.xscale('log')
        plt.yscale('log')
    if add_legend:
        plt.legend()
    if add_grid:
        plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
if __name__ == "__main__":
    # Example usage
    file_path = "./benchmarking/output/All Libraries Time Comparison/1/run.json"
    results = load_results(file_path)
    parsed_results, measurement_unit = parse_results(results)
    ordered_results = create_ordered_results(parsed_results)
    
    # Create plot from ordered results
    create_plot_from_results(ordered_results, measurement_unit)  # Add additional parameters as needed