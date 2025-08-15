from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVector as cv
import pygal as pg
import tracemalloc
import matplotlib.pyplot as plt
from plotly import graph_objects as go
import altair as alt
import pandas as pd
import pygal as pg
import numpy as np
exp_name = "Plotly Memory Allocation Problem"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    iterations = 1 
    cases = [
        {
            "option": "Plotly Line Plot",
            "input_type": "default"
        },
        {
            "option": "Plotly Line Plot - CompressedVector",
            "input_type": "default"
        }
    ]
    measurement_unit = "kilobytes"

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        if option == "Plotly Line Plot - CompressedVector":
            vecx = cv(decimal_places, width)
            vecx.create_vector(len(x))
            vecx.fill_from_vector(x)

            vecy = cv(decimal_places, width)
            vecy.create_vector(len(y))
            vecy.fill_from_vector(y)
            
            vecx.set_decompressed_config(True)
            vecy.set_decompressed_config(True)

            tracemalloc.start()

            x = np.asarray(x)
            y = np.asarray(y)
            fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
            fig.update_layout(title='Plotly Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')
            
        elif option == "Plotly Line Plot - CompressedVector":
            tracemalloc.start()
            fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
            fig.update_layout(title='Plotly Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak / 1024

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

