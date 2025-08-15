from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVectorDownsampler as cvd
import sdsl4py as sdsl
import time
import altair as alt
import pandas as pd 

exp_name = "CVD Decimal Places Build Time Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    decimal_places = [0, 1, 2,  5, 10]
    cases = []
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
        # Parsear la opción para obtener método, decimales y downsampler
        parts = option.split(" - ")
        method = parts[0]
        decimals = int(parts[1])
        downsampler = parts[2]
        
        # Medir tiempo de construcción del vector comprimido
        start_time = time.time()
        x_compressed, y_compressed = cvd().downsample(
                x=x, 
                y=y, 
                compress_method=method,
                method=downsampler,
                decimal_places=decimals,
                n_out=n_out
            )
        end_time = time.time()
        
        return end_time - start_time

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results
