import statistics
from sacred import Experiment
from sacred.observers import FileStorageObserver
from benchmarking.config import add_base_config, ROOT_OUTPUT_FOLDER
import gc

def setup_experiment(exp_name):
    exp = Experiment(exp_name)
    exp.observers.append(FileStorageObserver.create(ROOT_OUTPUT_FOLDER + "/" + exp_name))
    add_base_config(exp)
    return exp

def run_with_timing(input_handler_instance,
                    experiment_fn, 
                    cases, n_range, 
                    file_input_list, 
                    decimal_places, 
                    iterations, 
                    width, 
                    decompressed,
                    measurement_unit):
    results = {}

    for file_input in file_input_list:
        for n_size in n_range:
            for case in cases:
                option = case["option"]
                input_type = case["input_type"]
                compress_option = case.get("compress_option", None)
                downsampler = case.get("downsampler", None)
                n_out = case.get("n_out", None)

                try:
                    input_handler_instance.set_width(width, "y")
                    x, y = input_handler_instance.get_from_file(
                        file_path=file_input,
                        option=input_type,
                        decimal_places=decimal_places,
                        delimiter=";",
                        column=1,
                        truncate=n_size,
                        decompressed=decompressed,
                        compress_option=compress_option,
                        downsampler=downsampler,
                        n_out=n_out
                    )

                    if len(x) != len(y):
                        raise ValueError(
                            f"Length mismatch! {option=}, {file_input=}, {n_size=}, len(x)={len(x)}, len(y)={len(y)}"
                        )

                    differences = []
                    for _ in range(iterations):
                        differences.append(experiment_fn(x, y, option))

                    clean_file_input = file_input.split("/")[-1].split(".")[0]
                    key = f"{clean_file_input}_{n_size}_{option}"

                    results[key] = {
                        "option": option,
                        "file:": clean_file_input,
                        "n_size": n_size,
                        "mean": statistics.mean(differences),
                        "stdev": statistics.stdev(differences) if len(differences) > 1 else 0,
                        "min": min(differences),
                        "max": max(differences),
                        "all_differences": differences,
                        "iterations": iterations
                    }

                    del x
                    del y
                    gc.collect()

                except Exception as e:
                    print("💥 run_with_timing failed with:")
                    print(f"  option = {option}")
                    print(f"  input_type = {input_type}")
                    print(f"  file_input = {file_input}")
                    print(f"  n_size = {n_size}")
                    print(f"  compress_option = {compress_option}")
                    print(f"  downsampler = {downsampler}")
                    print(f"  n_out = {n_out}")
                    print(f"  decimal_places = {decimal_places}")
                    print(f"  width = {width}")
                    print(f"  iterations = {iterations}")
                    print(f"  decompressed = {decompressed}")
                    raise  # Re-raise to preserve original traceback
    return results

