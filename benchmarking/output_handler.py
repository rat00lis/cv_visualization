import json
import csv
import os

results_for_each_file = {}
experiment_title = "Untitled"  # will be overwritten


def get_raw_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def parse_results_from_file(file_read):
    global experiment_title
    results = json.loads(file_read)
    experiment_title = results.get("experiment", {}).get("name", "Untitled")
    result_data = results.get("result", {})

    for key, value in result_data.items():
        file_name = value.get("file:")
        n_size = value.get("n_size")

        if file_name is None or n_size is None:
            continue

        if file_name not in results_for_each_file:
            results_for_each_file[file_name] = {}
        if n_size not in results_for_each_file[file_name]:
            results_for_each_file[file_name][n_size] = []

        results_for_each_file[file_name][n_size].append(value)

def create_tables_from_results(output_folder):
    table_folder = os.path.join(output_folder, "tables")
    # Remove existing tables folder if it exists
    if os.path.exists(table_folder):
        import shutil
        shutil.rmtree(table_folder)
    os.makedirs(table_folder, exist_ok=True)

    # Rest of the function remains the same
    for file_name in results_for_each_file:
        file_path = os.path.join(table_folder, f"{file_name}.csv")
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["n_size", "option", "measurement_unit", "mean"])
            for n_size, measurements in results_for_each_file[file_name].items():
                for measurement in measurements:
                    writer.writerow([
                        n_size,
                        measurement.get("option"),
                        measurement.get("measurement_unit"),
                        measurement.get("mean")
                    ])
        print(f"Table created for {file_name} at {file_path}")


def create_plots_from_results(output_folder):
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Create folders for static and interactive plots
    plot_folder = os.path.join(output_folder, "plots")
    html_folder = os.path.join(output_folder, "htmls")
    
    # Remove existing folders if they exist
    for folder in [plot_folder, html_folder]:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    
    for file_name, n_size_dict in results_for_each_file.items():
        option_data = {}
        measurement_unit = None
        n_out = None
        
        for n_size, measurements in n_size_dict.items():
            for measurement in measurements:
                option = measurement.get("option")
                mean = measurement.get("mean")
                # Get the measurement unit from the first measurement
                if measurement_unit is None:
                    measurement_unit = measurement.get("measurement_unit")
                # Get n_out if available
                if n_out is None:
                    n_out = measurement.get("n_out")
                if option not in option_data:
                    option_data[option] = []
                option_data[option].append((n_size, mean))

        # Generate both normal and log scale plots with matplotlib
        for scale in ["linear", "log"]:
            plt.figure(figsize=(16, 9))  # 16:9 aspect ratio for a full-screen experience
            for option, points in option_data.items():
                sorted_points = sorted(points, key=lambda x: x[0])
                x = [p[0] for p in sorted_points]
                y = [p[1] for p in sorted_points]
                plt.plot(x, y, marker='o', label=option)

            # Add n_out to x label if it's not None
            n_out_text = f" (n_out={n_out})" if n_out is not None else ""
            plt.title(f"{experiment_title}\n{file_name}({scale} scale)")
            plt.xlabel("Number of Points" + n_out_text)
            
            # Set y-axis label based on measurement unit
            if measurement_unit == "seconds":
                plt.ylabel("Time (seconds)")
            else:
                plt.ylabel(f"Memory ({measurement_unit})")
                
            plt.yscale(scale)
            
            # Handle legend placement for many lines
            if len(option_data) > 10:
                # Place legend outside the plot to the right
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
            elif len(option_data) > 5:
                # Use a smaller font size for medium number of lines
                plt.legend(fontsize='small')
            else:
                plt.legend()
                
            plt.grid(True)
            plt.tight_layout()

            suffix = "" if scale == "linear" else "_log"
            path = f"{plot_folder}/{file_name}{suffix}.png"
            plt.savefig(path, bbox_inches='tight')  # bbox_inches ensures legend is within figure bounds
            plt.close()
            print(f"Plot ({scale}) created for {file_name} at {path}")
        
        # Create interactive HTML plots with Plotly
        for scale in ["linear", "log"]:
            fig = make_subplots()
            
            for option, points in option_data.items():
                sorted_points = sorted(points, key=lambda x: x[0])
                x = [p[0] for p in sorted_points]
                y = [p[1] for p in sorted_points]
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode='lines+markers',
                        name=option,
                        hovertemplate='Points: %{x}<br>Value: %{y:.6f}'
                    )
                )
            
            n_out_text = f" (n_out={n_out})" if n_out is not None else ""
            
            # Set titles and labels
            fig.update_layout(
                title=f"{experiment_title}<br>{file_name} ({scale} scale)",
                xaxis_title=f"Number of Points{n_out_text}",
                yaxis_title="Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})",
                hovermode="closest",
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                template="plotly_white"
            )
            
            # Apply log scale if needed
            if scale == "log":
                fig.update_layout(yaxis_type="log")
            
            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            
            # Save as HTML
            suffix = "" if scale == "linear" else "_log"
            html_path = f"{html_folder}/{file_name}{suffix}.html"
            fig.write_html(html_path, full_html=True, include_plotlyjs='cdn')
            print(f"Interactive plot ({scale}) created for {file_name} at {html_path}")

def handle_all_experiments():
    global results_for_each_file, experiment_title
    experiments_base_folder = "benchmarking/output/"
    
    try:
        for exp_name in os.listdir(experiments_base_folder):
            try:
                exp_folder = os.path.join(experiments_base_folder, exp_name)
                run_json_path = os.path.join(exp_folder, "1", "run.json")
                
                if os.path.exists(run_json_path):
                    try:
                        # Reset global variables for each experiment
                        results_for_each_file = {}
                        experiment_title = "Untitled"
                        
                        file_read = get_raw_from_file(run_json_path)
                        parse_results_from_file(file_read)
                        
                        # Use experiment name in output paths
                        output_folder = os.path.join(experiments_base_folder, exp_name)
                        create_tables_from_results(output_folder)
                        create_plots_from_results(output_folder)
                        
                        print(f"Processed experiment: {exp_name}")
                    except Exception as e:
                        print(f"Error processing experiment {exp_name}: {e}")
            except Exception as e:
                print(f"Error with experiment folder {exp_name}: {e}")
    except Exception as e:
        print(f"Error accessing experiments folder: {e}")

if __name__ == "__main__":
    handle_all_experiments()