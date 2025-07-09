from benchmarking import setup_experiment, run_with_timing
from input_handler import InputHandler

exp_name = "TEMPLATE"
exp = setup_experiment(exp_name)


@exp.config
def default_config():
    cases = [
        {
            "option": "Title 01",
            "input_type": "default"
        },
        {
            "option": "Title 02",
            "input_type": "compressed_vector",
            "compress_option": "enc_vector_elias_gamma"
        },
        {
            "option": "Title 03",
            "input_type": "compressed_vector_downsampler",
            "downsampler": "LTTBDownsampler",
            "compress_option": "enc_vector_elias_gamma",
            "n_out": 1000
        },
        {
            "option": "Title 04",
            "input_type": "tsdownsample",
            "downsampler": "LTTBDownsampler"
        }
    ]
    n_range = list(range(10000, 350000, 10000))

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        return

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed, measurement_unit, n_out)
    exp.log_scalar("num_cases", len(results))
    return results

