# from benchmarking.exp_runner import setup_experiment, run_with_timing
# from benchmarking.input_handler import InputHandler
# from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS
# import time


# exp_name = "Compression Time Comparison"
# exp = setup_experiment(exp_name)


# @exp.config
# def default_config():
#     n_outs = [100, 1000, 10000]
#     cases = [
#         {
#             "option": "Original Data",
#             "input_type": "default"
#         }
#     ]
#     for n_out in n_outs:
#         for method in COMPRESSION_METHODS:
#             cases.append({
#                 "option": f"Compressed Vector - {method}",
#                 "input_type": "default",
#                 "compress_option": method,
#                 "n_out": n_out
#             })
#             for downsampler in DOWNSAMPLERS:
#                 cases.append({
#                     "option": f"Compressed Vector Downsampler - {downsampler} - {method}",
#                     "input_type": "default",
#                     "downsampler": DOWNSAMPLERS[downsampler],
#                     "compress_option": method,
#                     "n_out": n_out
#                 })
#                 cases.append({
#                     "option": f"TS Downsample - {downsampler}",
#                     "input_type": "default",
#                     "downsampler": DOWNSAMPLERS[downsampler],
#                     "n_out": n_out
#                 })

        

# @exp.automain
# def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed):
#     input_handler_instance = InputHandler()

#     def experiment_fn(x, y, option):
#         #when option starts with
#         if option.startswith("Compressed Vector") or option.startswith("Compressed Vector Downsampler"):
#             start = time.perf_counter()
#             input_handler_instance.compress_vector(x, y, option)
#         elif option.startswith("TS Downsample"):
#             start = time.perf_counter()
#             input_handler_instance.ts_downsample(x, y, option)
#         else:
#             start = time.perf_counter()
#             input_handler_instance.default_input(x, y, option)

#         end = time.perf_counter()
#         return end - start

#     results = run_with_timing(input_handler_instance, experiment_fn, cases, n_range, file_input_list, decimal_places, iterations, width, decompressed)
#     exp.log_scalar("num_cases", len(results))
#     return results

editar 