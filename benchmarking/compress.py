from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVector, CompressedVectorDownsampler
import tsdownsample as tsd
import sdsl4py
import time
import numpy as np

exp_name = "Building Time Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    cases = [
        {
            "option": "Original Data",
            "input_type": "default"
        }
    ]
    # Add compressed vector downsampler cases - needs both compression method and downsampler
    for method in COMPRESSION_METHODS:
        # cases.append({
        #     "option": f"Compressed Vector - {method}",
        #     "input_type": "default"
        # })
        # cases.append({
        #     "option": f"SDSL4Py - {method}",
        #     "input_type": "default"
        # })
        for downsampler in DOWNSAMPLERS:
            cases.append({
                "option": f"Compressed Vector Downsampler - {downsampler} - {method}",
                "input_type": "default"
            })
    
    # Add TS Downsample cases separately - only needs downsampler
    for downsampler in DOWNSAMPLERS:
        cases.append({
            "option": f"TS Downsample - {downsampler}",
            "input_type": "default"
        })

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        try:
            start = 0
            if option.startswith("Compressed Vector Downsampler"):
                
                parts = option.split(" - ")
                if len(parts) < 3:
                    raise ValueError(f"Invalid option format: {option}")
                downsampler = DOWNSAMPLERS[parts[1]]
                compress_method = COMPRESSION_METHODS.get(parts[2], None)
                start = time.perf_counter()
                cx, cy = CompressedVectorDownsampler().downsample(
                    x=x,
                    y=y,
                    n_out=n_out,
                    method=downsampler,
                    compress_method=compress_method,
                    int_width=width
                )
            elif option.startswith("Compressed Vector"):
                start = time.perf_counter()
                parts = option.split(" - ")
                if len(parts) < 2:
                    raise ValueError(f"Invalid option format: {option}")
                compress_method = COMPRESSION_METHODS.get(parts[1], None)
                cx = CompressedVector(
                    decimal_places=decimal_places,
                    int_width=width
                )
                cy = CompressedVector(
                    decimal_places=decimal_places,
                    int_width=width
                )
                cx.create_vector(len(x))
                cy.create_vector(len(y))
                cx.fill_from_vector(x)
                cy.fill_from_vector(y)
                cx.compress(compress_method)
                cy.compress(compress_method)

            elif option.startswith("TS Downsample"):
                start = time.perf_counter()
                parts = option.split(" - ")
                if len(parts) < 2:
                    raise ValueError(f"Invalid option format: {option}")
                downsampler = DOWNSAMPLERS[parts[1]]
                indices = downsampler().downsample(
                    x, y,
                    n_out=n_out
                )
                indices = np.asarray(indices, dtype=int)
                x = np.asarray(x, dtype=np.float64) if x is not None else None
                y = np.asarray(y, dtype=np.float64) if y is not None else None
                cx = x[indices] if x is not None else None
                cy = y[indices] if y is not None else None
            elif option.startswith("SDSL4Py"):
                start = time.perf_counter()
                parts = option.split(" - ")
                if len(parts) < 2:
                    raise ValueError(f"Invalid option format: {option}")
                compress_method = COMPRESSION_METHODS.get(parts[1], None)
                if compress_method is None:
                    return 0  # No compression method specified
                x_vector = sdsl4py.int_vector(len(x), int_width=width)
                y_vector = sdsl4py.int_vector(len(y), int_width=width)
                for i in range(len(x)):
                    x_vector[i] = abs(int(x[i]))
                for i in range(len(y)):
                    y_vector[i] = abs(int(y[i]))
                compressed_x = compress_method(x_vector)
                compressed_y = compress_method(y_vector)
                cx, cy = compressed_x, compressed_y
            else:
                start = time.perf_counter()
                cx, cy = x, y  # Default case for "Original Data"

            end = time.perf_counter()
            return end - start
        except Exception as e:
            print(f"Error during case handling: {e}")
            return None

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results
