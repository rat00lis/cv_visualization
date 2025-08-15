from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, CompressedVector, CompressedVectorDownsampler
import tsdownsample
import sdsl4py
import time
import pandas as pd
import pygal as plg

exp_name = "Pygal Plotting Memory Allocation"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    iterations = 1
    cases = [
        {
            "option": "Original Data",
            "input_type": "default"
        }
    ]
    for method in COMPRESSION_METHODS:
        cases.append({
            "option": f"Compressed Vector Downsample - {method}",
            "input_type": "compressed_vector_downsampler",
            "compress_option": method
        })
    cases.append({
        "option": "TS Downsample",
        "input_type": "tsdownsample"
    })
    measurement_unit = "kilobytes"
    

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        import tracemalloc
        tracemalloc.start()

        try:
            line_plot = plg.Line()
            line_plot.title = f'Data Plot - {option}'
            line_plot.x_labels = map(str, range(len(x)))
            line_plot.add('Data', y)
            #render
            line_plot.render(is_unicode=True)
            current, peak = tracemalloc.get_traced_memory()
        except Exception as e:
            print(f"Error during processing: {e}")
            current, peak = 0, 0
        finally:
            tracemalloc.stop()

        return peak / 1024  # Return memory usage in kilobytes

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

