from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVector
import numpy as np
import pandas as pd
import sys
exp_name = "Comparison of Space Used"
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
            "compress_option": method,
            "n_out": 1000  
        })
    cases.append({
        "option": "TS Downsample",
        "input_type": "tsdownsample",
        "n_out": 1000
    })


@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        size_bytes = 0
        if isinstance(x, CompressedVector) and isinstance(y, CompressedVector):
            size_bytes = x.size_in_bytes() + y.size_in_bytes()
        elif isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            size_bytes = sys.getsizeof(x) + sys.getsizeof(y)
        else:
            size_bytes = 0
        # Ensure we always return size in bytes (positive integer)
        return int(size_bytes) if size_bytes >= 0 else 0

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

