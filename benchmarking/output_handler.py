import json
import csv
import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px  # NEW
from plotly.subplots import make_subplots

results_for_each_file = {}
experiment_title = "Untitled"  # will be overwritten

# NEW: extended color pool
color_pool = (
    px.colors.qualitative.Plotly +
    px.colors.qualitative.D3 +
    px.colors.qualitative.Alphabet +
    px.colors.qualitative.Set3
)

# Update the base output folder
OUTPUT_BASE_FOLDER = "OUTPUT"


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

def create_tables_from_results(output_folder, exp_name):
    table_folder = os.path.join(OUTPUT_BASE_FOLDER, exp_name, "tables")
    if os.path.exists(table_folder):
        shutil.rmtree(table_folder)
    os.makedirs(table_folder, exist_ok=True)

    for file_name in results_for_each_file:
        output_file_name = f"{exp_name}_{file_name}.csv"
        file_path = os.path.join(table_folder, output_file_name)
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

def create_line_plots(file_name, option_data, experiment_title, measurement_unit, n_out, show_n_out, output_folder, exp_name):
    for scale in ["linear", "log"]:
        plt.figure(figsize=(16, 9))
        for option, points in option_data.items():
            sorted_points = sorted(points, key=lambda x: x[0])
            x = [p[0] for p in sorted_points]
            y = [p[1] for p in sorted_points]
            plt.plot(x, y, marker='o', label=option)

        n_out_text = f" (n_out={n_out})" if show_n_out and n_out is not None else ""
        plt.title(f"{experiment_title}\n{file_name} (line, {scale} scale)")
        plt.xlabel("Number of Points" + n_out_text)
        plt.ylabel("Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})")
        plt.yscale(scale)

        if len(option_data) > 10:
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
        elif len(option_data) > 5:
            plt.legend(fontsize='small')
        else:
            plt.legend()

        plt.grid(True)
        plt.tight_layout()
        suffix = "" if scale == "linear" else "_log"
        output_file_name = f"{exp_name}_{file_name}{suffix}.png"
        path = os.path.join(output_folder, output_file_name)
        plt.savefig(path, bbox_inches='tight')
        plt.close()

        fig = go.Figure()
        for i, (option, points) in enumerate(option_data.items()):
            sorted_points = sorted(points, key=lambda x: x[0])
            x = [p[0] for p in sorted_points]
            y = [p[1] for p in sorted_points]
            if scale == "log":
                filtered = [(a, b) for a, b in zip(x, y) if b > 0]
                if not filtered:
                    continue
                x, y = zip(*filtered)
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=option,
                line=dict(color=color_pool[i % len(color_pool)])
            ))

        fig.update_layout(
            title=f"{experiment_title}<br>{file_name} ({scale} scale)",
            xaxis_title=f"Number of Points{n_out_text}",
            yaxis_title="Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})",
            hovermode="closest",
            template="plotly_white"
        )
        if scale == "log":
            fig.update_layout(yaxis_type="log")

        html_file_name = f"{exp_name}_{file_name}{suffix}.html"
        html_path = os.path.join(output_folder, html_file_name)
        fig.write_html(html_path, full_html=True, include_plotlyjs='cdn')

def create_bar_plots(file_name, option_data, experiment_title, measurement_unit, n_out, show_n_out, output_folder, exp_name):
    for scale in ["linear", "log"]:
        plt.figure(figsize=(16, 9))
        bar_width = 0.8 / len(option_data)
        all_x = sorted({p[0] for points in option_data.values() for p in points})
        for i, (option, points) in enumerate(option_data.items()):
            sorted_points = sorted(points, key=lambda x: x[0])
            x_vals = [p[0] for p in sorted_points]
            y_vals = [p[1] for p in sorted_points]
            x_indices = [all_x.index(x) + i * bar_width for x in x_vals]
            plt.bar(x_indices, y_vals, width=bar_width, label=option)
        tick_positions = [i + bar_width * (len(option_data) / 2 - 0.5) for i in range(len(all_x))]
        plt.xticks(tick_positions, all_x)

        n_out_text = f" (n_out={n_out})" if show_n_out and n_out is not None else ""
        plt.title(f"{experiment_title}\n{file_name} (bar, {scale} scale)")
        plt.xlabel("Number of Points" + n_out_text)
        plt.ylabel("Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})")
        plt.yscale(scale)

        if len(option_data) > 10:
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
        elif len(option_data) > 5:
            plt.legend(fontsize='small')
        else:
            plt.legend()

        plt.grid(True, axis='y')
        plt.tight_layout()
        suffix = "_bar" if scale == "linear" else "_bar_log"
        output_file_name = f"{exp_name}_{file_name}{suffix}.png"
        path = os.path.join(output_folder, output_file_name)
        plt.savefig(path, bbox_inches='tight')
        plt.close()

        fig = go.Figure()
        for i, (option, points) in enumerate(option_data.items()):  # NEW
            sorted_points = sorted(points, key=lambda x: x[0])
            x = [p[0] for p in sorted_points]
            y = [p[1] for p in sorted_points]
            if scale == "log":
                filtered = [(a, b) for a, b in zip(x, y) if b > 0]
                if not filtered:
                    continue
                x, y = zip(*filtered)
            fig.add_trace(go.Bar(
                x=x,
                y=y,
                name=option,
                marker_color=color_pool[i % len(color_pool)]  # NEW
            ))

        fig.update_layout(
            title=f"{experiment_title}<br>{file_name} ({scale} scale)",
            xaxis_title=f"Number of Points{n_out_text}",
            yaxis_title="Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})",
            hovermode="closest",
            template="plotly_white",
            barmode="group",
            bargap=0.05,
            bargroupgap=0.05,
            width=1800,
            height=900,
            xaxis=dict(type='category')
        )
        if scale == "log":
            fig.update_layout(yaxis_type="log")

        html_file_name = f"{exp_name}_{file_name}{suffix}.html"
        html_path = os.path.join(output_folder, html_file_name)
        fig.write_html(html_path, full_html=True, include_plotlyjs='cdn')

# Modify create_plots_from_results to organize plots in the HTML with proper titles and spacing
def create_plots_from_results(output_folder, exp_name, show_n_out=True):
    line_plot_folder = os.path.join(OUTPUT_BASE_FOLDER, exp_name, "plots")
    bar_plot_folder = os.path.join(OUTPUT_BASE_FOLDER, exp_name, "bar_plots")
    consolidated_html_path = os.path.join(OUTPUT_BASE_FOLDER, exp_name, f"{exp_name}_all_plots.html")

    for folder in [line_plot_folder, bar_plot_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

    # Create a list to store HTML sections for each plot
    html_sections = []

    for file_name, n_size_dict in results_for_each_file.items():
        option_data = {}
        measurement_unit = None
        n_out = None

        for n_size, measurements in n_size_dict.items():
            for measurement in measurements:
                option = measurement.get("option")
                mean = measurement.get("mean")
                if measurement_unit is None:
                    measurement_unit = measurement.get("measurement_unit")
                if n_out is None:
                    n_out = measurement.get("n_out")
                option_data.setdefault(option, []).append((n_size, mean))

        for scale in ["linear", "log"]:
            # Generate static line plots using Matplotlib
            plt.figure(figsize=(16, 9))
            for option, points in option_data.items():
                sorted_points = sorted(points, key=lambda x: x[0])
                x = [p[0] for p in sorted_points]
                y = [p[1] for p in sorted_points]
                plt.plot(x, y, marker='o', label=option)

            n_out_text = f" (n_out={n_out})" if show_n_out and n_out is not None else ""
            plt.title(f"{experiment_title}\n{file_name} (line, {scale} scale)")
            plt.xlabel(f"Number of Points{n_out_text}")
            plt.ylabel("Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})")
            plt.yscale(scale)
            plt.grid(True)
            plt.tight_layout(rect=[0, 0.1, 1, 0.95])  # Adjust layout to make space for legend
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)  # Move legend to bottom

            line_plot_path = os.path.join(line_plot_folder, f"{exp_name}_{file_name}_{scale}_line.png")
            plt.savefig(line_plot_path, bbox_inches='tight')
            plt.close()

            # Add interactive line plot to HTML sections using Plotly
            fig_line = go.Figure()
            for option, points in option_data.items():
                sorted_points = sorted(points, key=lambda x: x[0])
                x = [p[0] for p in sorted_points]
                y = [p[1] for p in sorted_points]
                fig_line.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='lines+markers',
                    name=option,
                    line=dict(color=color_pool[len(fig_line.data) % len(color_pool)])
                ))

            fig_line.update_layout(
                title=f"{experiment_title}<br>{file_name} (line, {scale} scale)",
                xaxis_title=f"Number of Points{n_out_text}",
                yaxis_title="Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})",
                hovermode="closest",
                template="plotly_white",
                yaxis_type="log" if scale == "log" else "linear"
            )

            html_sections.append(f"<h2>{file_name} (line, {scale} scale)</h2>")
            html_sections.append(fig_line.to_html(full_html=False, include_plotlyjs=False))

            # Generate static bar plots using Matplotlib
            plt.figure(figsize=(16, 9))
            bar_width = 0.8 / len(option_data)
            all_x = sorted({p[0] for points in option_data.values() for p in points})
            for i, (option, points) in enumerate(option_data.items()):
                sorted_points = sorted(points, key=lambda x: x[0])
                x_vals = [p[0] for p in sorted_points]
                y_vals = [p[1] for p in sorted_points]
                x_indices = [all_x.index(x) + i * bar_width for x in x_vals]
                plt.bar(x_indices, y_vals, width=bar_width, label=option)
            tick_positions = [i + bar_width * (len(option_data) / 2 - 0.5) for i in range(len(all_x))]
            plt.xticks(tick_positions, all_x)

            plt.title(f"{experiment_title}\n{file_name} (bar, {scale} scale)")
            plt.xlabel(f"Number of Points{n_out_text}")
            plt.ylabel("Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})")
            plt.yscale(scale)
            plt.grid(True, axis='y')
            plt.tight_layout(rect=[0, 0.1, 1, 0.95])  # Adjust layout to make space for legend
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)  # Move legend to bottom

            bar_plot_path = os.path.join(bar_plot_folder, f"{exp_name}_{file_name}_{scale}_bar.png")
            plt.savefig(bar_plot_path, bbox_inches='tight')
            plt.close()

            # Add interactive bar plot to HTML sections using Plotly
            fig_bar = go.Figure()
            for option, points in option_data.items():
                sorted_points = sorted(points, key=lambda x: x[0])
                x = [p[0] for p in sorted_points]
                y = [p[1] for p in sorted_points]
                fig_bar.add_trace(go.Bar(
                    x=x,
                    y=y,
                    name=option,
                    marker_color=color_pool[len(fig_bar.data) % len(color_pool)]
                ))

            fig_bar.update_layout(
                title=f"{experiment_title}<br>{file_name} (bar, {scale} scale)",
                xaxis_title=f"Number of Points{n_out_text}",
                yaxis_title="Time (seconds)" if measurement_unit == "seconds" else f"Memory ({measurement_unit})",
                hovermode="closest",
                template="plotly_white",
                barmode="group",
                yaxis_type="log" if scale == "log" else "linear"
            )

            html_sections.append(f"<h2>{file_name} (bar, {scale} scale)</h2>")
            html_sections.append(fig_bar.to_html(full_html=False, include_plotlyjs=False))

    # Write the consolidated HTML file
    with open(consolidated_html_path, "w") as html_file:
        html_file.write("<html><head><script src='https://cdn.plot.ly/plotly-latest.min.js'></script></head><body>")
        html_file.write("<h1>All Plots for Experiment: {}</h1>".format(exp_name))
        html_file.write("<div style='margin-bottom: 50px;'>" + "\n".join(html_sections) + "</div>")
        html_file.write("</body></html>")

    print(f"Consolidated HTML created at {consolidated_html_path}")

# Update handle_all_experiments to remove the bar parameter
def handle_all_experiments(json_filter_path=None, show_n_out=True):
    experiments_base_folder = "benchmarking/output/"
    exp_filter = None
    if json_filter_path and os.path.exists(json_filter_path):
        with open(json_filter_path, "r") as f:
            exp_filter = json.load(f).get("exp_to_run", {})

    for exp_name in os.listdir(experiments_base_folder):
        if exp_filter and exp_name not in exp_filter:
            print(f"Skipping folder {exp_name} (not in filter)")
            continue

        exp_folder = os.path.join(experiments_base_folder, exp_name)
        run_subfolders = [d for d in os.listdir(exp_folder) if d.isdigit()]
        if not run_subfolders:
            print(f"No run folders found in {exp_name}")
            continue
        latest_run = max(map(int, run_subfolders))
        run_json_path = os.path.join(exp_folder, str(latest_run), "run.json")

        if not os.path.exists(run_json_path):
            print(f"No run.json in {exp_name}/run {latest_run}")
            continue

        try:
            global results_for_each_file, experiment_title
            results_for_each_file = {}
            experiment_title = "Untitled"

            file_read = get_raw_from_file(run_json_path)
            parse_results_from_file(file_read)

            allowed_options = exp_filter.get(exp_name, {}).get("options", []) if exp_filter else None

            if allowed_options:
                for file_key in list(results_for_each_file.keys()):
                    for n_size in list(results_for_each_file[file_key].keys()):
                        results_for_each_file[file_key][n_size] = [
                            m for m in results_for_each_file[file_key][n_size]
                            if m.get("option") in allowed_options
                        ]
                        if not results_for_each_file[file_key][n_size]:
                            del results_for_each_file[file_key][n_size]
                    if not results_for_each_file[file_key]:
                        del results_for_each_file[file_key]

            if not results_for_each_file:
                print(f"Skipping {exp_name} (no matching results after filtering)")
                continue

            output_folder = os.path.join(OUTPUT_BASE_FOLDER, exp_name)
            create_tables_from_results(output_folder, exp_name)
            create_plots_from_results(output_folder, exp_name, show_n_out)

            print(f"Processed experiment: {exp_name}")
        except Exception as e:
            print(f"Error processing experiment in folder {exp_name}: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process experiment results and generate plots')
    parser.add_argument('json_filter', nargs='?', default=None,
                        help='Path to JSON filter file')
    parser.add_argument('--no-n-out', action='store_true',
                        help='Hide n_out labels from plots (default: show n_out)')
    args = parser.parse_args()

    show_n_out = not args.no_n_out

    handle_all_experiments(args.json_filter, show_n_out)
