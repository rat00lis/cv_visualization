from benchmarking import setup_experiment, run_with_timing
from input_handler import InputHandler

# Override default config
# @exp.config
# def default_config():
#     cases = [
#         {
#             "option": "plotly_resampler",
#             "input_type": "default",
#         },
#         {
#             "option": "sdsl4py",
#             "input_type": "sdsl4py",
#         }
#     ]
#     n_range = list(range(10000, 350000, 10000))

exp_name = "TEMPLATE"
exp = setup_experiment(exp_name)

@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed):
    input_handler_instance = InputHandler()

    def experiment_fn(x, y, option):
        return

    results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed)
    exp.log_scalar("num_cases", len(results))
    return results

