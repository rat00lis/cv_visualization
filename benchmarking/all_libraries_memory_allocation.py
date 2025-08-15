from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVectorDownsampler
import pygal as pg
import tracemalloc
import matplotlib.pyplot as plt
from plotly import graph_objects as go
import altair as alt
import pandas as pd
import pygal as pg
import numpy as np
exp_name = "All Libraries Memory Allocation"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    iterations = 1
    cases = [
        {
            "option": "MatPlotlib Line Plot",
            "input_type": "default"
        },
        {
            "option": "Plotly Line Plot",
            "input_type": "default"
        },
        {
            "option": "Altair Line Plot",
            "input_type": "compressed_vector_downsampler"
        },
        {
            "option": "Pygal Line Plot",
            "input_type": "default"
        }
    ]
    measurement_unit = "kilobytes"

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):

        if option == "MatPlotlib Line Plot":
            cx, cy = CompressedVectorDownsampler().downsample(x,y,n_out=n_out)
            cx.set_decompressed_config(True)
            cy.set_decompressed_config(True)

            tracemalloc.start()

            x = np.asarray(cx)
            y = np.asarray(cy)

            plt.figure(figsize=(width, 6))
            plt.plot(x, y, label='Data')
            plt.title('Matplotlib Line Plot')
            plt.xlabel('X-axis')
            plt.ylabel('Y-axis')
            plt.legend()
            plt.close()
            
        elif option == "Plotly Line Plot":
            cx, cy = CompressedVectorDownsampler().downsample(x,y,n_out=n_out)
            cx.set_decompressed_config(True)
            cy.set_decompressed_config(True)

            tracemalloc.start()

            x = np.asarray(cx)
            y = np.asarray(cy)
            
            df = pd.DataFrame({'x': x, 'y': y})

            pd.options.plotting.backend = "plotly"
            fig = df.plot()
            fig.update_layout(title='Plotly Line Plot', xaxis_title='X-axis', yaxis_title='Y-axis')
            
        elif option == "Altair Line Plot":
            tracemalloc.start()

            df = pd.DataFrame({'x': x, 'y': y})
            chart = alt.Chart(df).mark_line().encode(x='x', y='y').interactive()

        elif option == "Altair Line Plot - No CV":
            tracemalloc.start()

            df = pd.DataFrame({'x': x, 'y': y})
            chart = alt.Chart(df).mark_line().encode(x='x', y='y').interactive()
            
        elif option == "Pygal Line Plot":
            cx, cy = CompressedVectorDownsampler().downsample(x,y,n_out=n_out)
            cx.set_decompressed_config(True)
            cy.set_decompressed_config(True)

            tracemalloc.start()
            line_plot = pg.Line()
            line_plot.title = 'Pygal Line Plot'
            line_plot.x_labels = map(str, range(len(cx)))
            line_plot.add('Data', list(cy))
            
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak / 1024

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

