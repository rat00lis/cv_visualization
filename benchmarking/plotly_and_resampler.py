from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVector as cv
import pygal as pg
from plotly_resampler import FigureWidgetResampler 
import time
import matplotlib.pyplot as plt
from plotly import graph_objects as go
import altair as alt
import pandas as pd
import pygal as pg
import numpy as np
exp_name = "Plotly vs Plotly-Resampler"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    cases = [
        {
            "option": "Plotly",
            "input_type": "default"
        },
        {
            "option": "Plotly-Resampler",
            "input_type": "default"
        }
    ]

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        start = time.perf_counter()
        
        if option == "Plotly":
            # Standard Plotly plotting
            fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
            fig.update_layout(title='Plotly Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')
            
        elif option == "Plotly-Resampler":
            # Use FigureWidgetResampler for resampling capabilities
            # Sort data by x-values for plotly-resampler requirement

            fig = FigureWidgetResampler(go.Figure())
            fig.add_trace(go.Scattergl(name='noisy sine', showlegend=True), hf_x=x, hf_y=y)
        
        end = time.perf_counter()
        return end - start

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

