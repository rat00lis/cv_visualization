from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVectorDownsampler as cvd
import sdsl4py as sdsl
import time
import altair as alt
import pandas as pd 

exp_name = "CVD Decimal Places Access Time Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    decimal_places = [0, 1, 2,  5, 10]
    cases = [
        {
            "option": "Original Data",
            "input_type": "default"
        }
    ]
    for method in COMPRESSION_METHODS:
        for downsampler in DOWNSAMPLERS:
            for decimals in decimal_places:
                cases.append({
                    "option": f"{method} - {decimals} - {downsampler}",
                    "input_type": "default"
                })

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        try:
            if option == "Original Data":
                # Measure access time for each element in original data
                access_times = []
                for i in range(len(y)):
                    start_time = time.time()
                    _ = y[i]
                    end_time = time.time()
                    access_times.append(end_time - start_time)
                return sum(access_times) / len(access_times)  # Return average access time
            else:
                # Parse the option to get method, decimals, and downsampler
                parts = option.split(" - ")
                method = parts[0]
                decimals = int(parts[1])
                downsampler = parts[2]
                
                # Create the compressed vector with downsampling
                x, y = cvd().downsample(
                    x=x, 
                    y=y, 
                    compress_method=method,
                    method=downsampler,
                    decimal_places=decimals,
                    n_out=n_out
                )
                
                # Measure access time for each element in the compressed vector
                access_times = []
                for i in range(len(y)):
                    start_time = time.time()
                    _ = y[i]
                    end_time = time.time()
                    access_times.append(end_time - start_time)
                
                return sum(access_times) / len(access_times)  # Return average access time
        except Exception as e:
            print(f"Error in experiment_fn with option '{option}': {e}")
            return None

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results
