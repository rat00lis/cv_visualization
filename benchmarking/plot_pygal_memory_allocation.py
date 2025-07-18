from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS
import pygal as pg
import tracemalloc


exp_name = "PyGal Memory Allocation"
exp = setup_experiment(exp_name)

@exp.config
def default_config():
    measurement_unit = "kilobytes"
    iterations = 1 
    n_outs = [1000]
    cases = [
        {
            "option": "Original Data",
            "input_type": "default"
        }
    ]
    for n_out in n_outs:
        for method in COMPRESSION_METHODS:
            cases.append({
                "option": f"Compressed Vector - {method} - {n_out}",
                "input_type": "compressed_vector",
                "compress_option": method,
                "n_out": n_out
            })
            for downsampler in DOWNSAMPLERS:
                cases.append({
                    "option": f"Compressed Vector Downsampler - {downsampler} - {method} - {n_out}",
                    "input_type": "compressed_vector_downsampler",
                    "downsampler": DOWNSAMPLERS[downsampler],
                    "compress_option": method,
                    "n_out": n_out
                })
                cases.append({
                    "option": f"TS Downsample - {downsampler} - {n_out}",
                    "input_type": "tsdownsample",
                    "downsampler": DOWNSAMPLERS[downsampler],
                    "n_out": n_out
                })

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        tracemalloc.start()

        line_plot = pg.Line()
        line_plot.title = 'Original vs Compressed Vector'
        line_plot.x_labels = map(str, range(len(x)))
        line_plot.add('Compressed', list(y))

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak / 1024

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

