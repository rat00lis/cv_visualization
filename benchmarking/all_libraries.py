from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS
import pygal as pg
import time
import matplotlib.pyplot as plt
from plotly import graph_objects as go
import altair as alt
import pandas as pd
import pygal as pg
import numpy as np
exp_name = "All Libraries Time Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    cases = [
        {
            "option": "MatPlotlib Line Plot",
            "input_type": "compressed_vector_downsampler"
        },
        {
            "option": "Plotly Line Plot",
            "input_type": "compressed_vector_downsampler"
        },
        {
            "option": "Altair Line Plot",
            "input_type": "compressed_vector_downsampler"
        },
        {
            "option": "Pygal Line Plot",
            "input_type": "compressed_vector_downsampler"
        }
    ]

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        start = time.perf_counter()
        if option == "MatPlotlib Line Plot":
            x.set_decompressed_config(True)
            y.set_decompressed_config(True)
            x = np.asarray(x)
            y = np.asarray(y)
            plt.figure(figsize=(width, 6))
            plt.plot(x, y, label='Data')
            plt.title('Matplotlib Line Plot')
            plt.xlabel('X-axis')
            plt.ylabel('Y-axis')
            plt.legend()
            plt.close()
            
        elif option == "Plotly Line Plot":
            x.set_decompressed_config(True)
            y.set_decompressed_config(True)
            x = np.asarray(x)
            y = np.asarray(y)
            fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
            fig.update_layout(title='Plotly Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')
            
        elif option == "Altair Line Plot":
            df = pd.DataFrame({'x': x, 'y': y})
            chart = alt.Chart(df).mark_line().encode(x='x', y='y').interactive()
            
        elif option == "Pygal Line Plot":
            line_plot = pg.Line()
            line_plot.title = 'Pygal Line Plot'
            line_plot.x_labels = map(str, range(len(x)))
            line_plot.add('Data', list(y))
        
        end = time.perf_counter()
        return end - start
        

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

