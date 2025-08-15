from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, CompressedVector, CompressedVectorDownsampler
import tsdownsample
import sdsl4py
import time
import pygal as pg

exp_name = "PyGal Plotting + Building Comparison"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    cases = [
        {
            "option": "Original Data",
            "input_type": "default"
        }
    ]
    for method in COMPRESSION_METHODS:
        cases.append({
            "option": f"Compressed Vector Downsample - {method}",
            "input_type": "default"
        })
    cases.append({
        "option": "TS Downsample",
        "input_type": "default"
    })


@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        start = time.perf_counter()

        if option == "Original Data":
            # No processing, just use original data
            x_out = x
            y_out = y

        elif isinstance(option, str) and option.startswith("Compressed Vector - "):
            method = option.removeprefix("Compressed Vector - ")
            compress_fn = COMPRESSION_METHODS.get(method)
            if compress_fn is None:
                x_out = x
                y_out = y
            else:
                cv_x = CompressedVector(int_width=width, decimal_places=decimal_places)
                cv_x.create_vector(len(x))
                cv_x.fill_from_vector(x)
                cv_x.compress(compress_fn)

                cv_y = CompressedVector(int_width=width, decimal_places=decimal_places)
                cv_y.create_vector(len(y))
                cv_y.fill_from_vector(y)
                cv_y.compress(compress_fn)

                x_out, y_out = cv_x, cv_y

        elif isinstance(option, str) and option.startswith("SDSL4PY Vector - "):
            method = option.removeprefix("SDSL4PY Vector - ")
            compress_fn = COMPRESSION_METHODS.get(method)
            if compress_fn is None:
                x_out = x
                y_out = y
            else:
                sdsl4py_x = sdsl4py.int_vector(len(x), int_width=width)
                for i in range(len(x)):
                    sdsl4py_x[i] = abs(int(x[i]))
                sdsl4py_x_c = compress_fn(sdsl4py_x)

                sdsl4py_y = sdsl4py.int_vector(len(y), int_width=width)
                for i in range(len(y)):
                    sdsl4py_y[i] = abs(int(y[i]))
                sdsl4py_y_c = compress_fn(sdsl4py_y)

                x_out, y_out = sdsl4py_x_c, sdsl4py_y_c

        elif isinstance(option, str) and option.startswith("Compressed Vector Downsample - "):
            method = option.removeprefix("Compressed Vector Downsample - ")
            compress_fn = COMPRESSION_METHODS.get(method)
            if compress_fn is None:
                x_out = x
                y_out = y
            else:
                x_out, y_out = CompressedVectorDownsampler().downsample(
                    x=x,
                    y=y,
                    # n_out is 10% of the input length
                    n_out=1000,
                    int_width=width,
                    decimal_places=decimal_places,
                    compress_method=compress_fn
                )

        elif isinstance(option, str) and option.startswith("TS Downsample"):
            ds_instance = tsdownsample.MinMaxLTTBDownsampler()
            n_out = 1000

            indices = ds_instance.downsample(x, y, n_out=n_out)

            x_out = [x[i] for i in indices]
            y_out = [y[i] for i in indices]

        else:
            raise ValueError(f"Unknown option format: {option}")

        # Create PyGal line plot
        line_plot = pg.Line()
        line_plot.title = 'PyGal Plotting + Building Comparison'
        line_plot.x_labels = map(str, range(len(x_out)))
        line_plot.add('Data', list(y_out))

        end = time.perf_counter()
        return end - start

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results