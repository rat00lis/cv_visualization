from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVector, CompressedVectorDownsampler
import tsdownsample as tsd
import time
import numpy as np

exp_name = "Compression Time Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    n_outs = [100, 1000, 10000]
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
                "input_type": "default",
                "compress_option": method,
                "n_out": n_out
            })
            for downsampler in DOWNSAMPLERS:
                cases.append({
                    "option": f"Compressed Vector Downsampler - {downsampler} - {method} - {n_out}",
                    "input_type": "default",
                    "downsampler": DOWNSAMPLERS[downsampler],
                    "compress_option": method,
                    "n_out": n_out
                })
                cases.append({
                    "option": f"TS Downsample - {downsampler} - {n_out}",
                    "input_type": "default",
                    "downsampler": DOWNSAMPLERS[downsampler],
                    "n_out": n_out
                })

        

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        #when option starts with
        if option.startswith("Compressed Vector Downsampler"):
            start = time.perf_counter()
            cx, cy = CompressedVectorDownsampler().downsample(
                x=x,
                y=y,
                n_out=1000,
                method=DOWNSAMPLERS[option.split(" - ")[-3]],
                compress_method=COMPRESSION_METHODS.get(option.split(" - ")[-2], None)
            )
        elif option.startswith("Compressed Vector"):
            start = time.perf_counter()
            # create compressed vectors
            cx = CompressedVector(
                decimal_places=decimal_places,
                int_width=32
            )
            cy = CompressedVector(
                decimal_places=decimal_places,
                int_width=32
            )
            cx.create_vector(len(x))
            cy.create_vector(len(y))

            compress_method = COMPRESSION_METHODS.get(option.split(" - ")[-2], None)
            if compress_method is not None:
                cx.compress(compress_method)
                cy.compress(compress_method)

        elif option.startswith("TS Downsample"):
            start = time.perf_counter()
            indices = DOWNSAMPLERS[option.split(" - ")[-2]]().downsample(
                x, y,
                n_out=1000
            )
            indices = np.asarray(indices, dtype=int)
            x = np.asarray(x, dtype=np.float64) if x is not None else None
            y = np.asarray(y, dtype=np.float64) if y is not None else None
            cx = x[indices] if x is not None else None
            cy = y[indices] if y is not None else None
        else:
            start = time.perf_counter()

        end = time.perf_counter()
        return end - start

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results
