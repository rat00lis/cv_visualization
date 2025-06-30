from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, CompressedVector
import sdsl4py
import time

exp_name = "Time for building Compressed Vector and SDSL4PY Vector"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    cases = []
    for method in COMPRESSION_METHODS:
        cases.append({
            "option": f"Compressed Vector - {method}",
            "input_type": "default"
        })
        cases.append({
            "option": f"SDSL4PY Vector - {method}",
            "input_type": "default"
        })
    

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        compress_method = option.split(" - ")[-1] if " - " in option else None
        is_compressed_vector = "Compressed Vector" in option

        start = time.perf_counter()
        if is_compressed_vector:
            compressed_method_function = COMPRESSION_METHODS[compress_method]
            if compressed_method_function is not None:
                cv = CompressedVector(
                    int_width=width,
                    decimal_places=decimal_places)
                cv.create_vector(len(x))
                cv.fill_from_vector(x)
                cv.compress(compressed_method_function)
        else:
            compressed_method_function = COMPRESSION_METHODS[compress_method]
            if compressed_method_function is not None:
                normal_vec = sdsl4py.int_vector(len(x), int_width=width)
                for i in range(len(x)):
                    normal_vec[i] = abs(int(y[i]))
                compressed = compressed_method_function(normal_vec)
            
        end = time.perf_counter()
        elapsed_time = end - start
        return elapsed_time


    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit=measurement_unit)
    exp.log_scalar("num_cases", len(results))
    return results

