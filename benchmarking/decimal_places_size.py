from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVectorDownsampler as cvd
import sdsl4py as sdsl
import time
import altair as alt
import pandas as pd 

exp_name = "CVD Decimal Places Size Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    decimal_places = [0, 1, 2,  5, 10]
    iterations = 1
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
        if option == "Original Data":
            # Calcular tamaño en bytes de los datos originales
            # Asumiendo que son arrays de numpy float64 (8 bytes por elemento)
            import sys
            x_size = sys.getsizeof(x) if hasattr(x, '__len__') else len(x) * 8
            y_size = sys.getsizeof(y) if hasattr(y, '__len__') else len(y) * 8
            return x_size + y_size
        else:
            # Parsear la opción para obtener método, decimales y downsampler
            parts = option.split(" - ")
            method = parts[0]
            decimals = int(parts[1])
            downsampler = parts[2]
            
            # Crear el vector comprimido con downsampling
            x_compressed, y_compressed = cvd().downsample(
                x=x, 
                y=y, 
                compress_method=method,
                method=downsampler,
                decimal_places=decimals,
                n_out=n_out
            )
            
            # Obtener el tamaño en bytes de los vectores comprimidos
            x_size = x_compressed.size_in_bytes()
            y_size = y_compressed.size_in_bytes()
            
            return x_size + y_size

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results
