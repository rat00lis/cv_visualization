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
    measurement_unit = "bytes"
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
        size = -1
        if isinstance(x, CompressedVector) and isinstance(y, CompressedVector):
            size = x.size_in_bytes() + y.size_in_bytes()
        elif isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            size = x.nbytes + y.nbytes
        elif isinstance(x, pd.DataFrame) and isinstance(y, pd.DataFrame):
            size = x.memory_usage(deep=True).sum() + y.memory_usage(deep=True).sum()
        elif isinstance(x, list) and isinstance(y, list):
            size = sum(sys.getsizeof(item) for item in x) + sum(sys.getsizeof(item) for item in y)
        else:
            raise TypeError(f"Unsupported data types: {type(x)}, {type(y)}")
        return size

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

