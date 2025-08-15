import statistics
from sacred import Experiment
from sacred.observers import FileStorageObserver
from benchmarking.config import add_base_config, ROOT_OUTPUT_FOLDER, map_file_to_x_column, DECIMAL_PLACES, COLUMN, map_file_to_y_column, map_file_to_decimal_places
import gc
from tqdm import tqdm

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
                    measurement_unit,
                    n_out=None,
                    warm_up_iterations=1):  # Added warm-up parameter
    results = {}

    # Calculate total combinations for progress bar
    total_combinations = len(file_input_list) * len(n_range) * len(cases)
    
    with tqdm(total=total_combinations, desc="Running experiments", unit="combo") as pbar:
        for file_input in file_input_list:
            for n_size in n_range:
                for case in cases:
                    option = case["option"]
                    input_type = case["input_type"]
                    compress_option = case.get("compress_option", None)
                    downsampler = case.get("downsampler", None)
                    n_out = case.get("n_out", n_out)
                    x_column = case.get("x_column", get_x_column_from_file(file_input))
                    column = case.get("column", get_y_column_from_file(file_input))
                    decimal_places = case.get("decimal_places", get_decimal_places_from_file(file_input))

                    # Update progress bar description
                    clean_file_input = file_input.split("/")[-1].split(".")[0]
                    pbar.set_description(f"Processing {clean_file_input} | n={n_size} | {option}")

                    try:
                        if file_input == "./benchmarking/input/yellow_tripdata_2015-01.csv":
                            y_width = 8
                        else:
                            print(f"Using default width {width} for file {file_input}")
                            y_width = width
                        input_handler_instance.set_width(y_width, "y")
                        input_handler_instance.set_width(width, "x")
                        
                        # Build parameters dictionary with required parameters
                        params = {
                            "file_path": file_input,
                            "option": input_type,
                            "decimal_places": decimal_places,
                            "delimiter": ";",
                            "column": column,
                            "truncate": n_size,
                            "decompressed": decompressed,
                            "x_column": x_column
                        }
                        
                        # Add optional parameters only if they are not None
                        if n_out is not None:
                            params["n_out"] = n_out
                        if compress_option is not None:
                            params["compress_option"] = compress_option
                        if downsampler is not None:
                            params["downsampler"] = downsampler
                        
                        # Perform warm-up iterations
                        # print(f"Performing {warm_up_iterations} warm-up iterations for {option}...")
                        for _ in tqdm(range(warm_up_iterations), 
                                    desc="Warm-up", 
                                    leave=False, 
                                    disable=warm_up_iterations < 5):  # Only show if >= 5 iterations
                            x_warmup, y_warmup = input_handler_instance.get_from_file(**params)
                            _ = experiment_fn(x_warmup, y_warmup, option)
                            del x_warmup
                            del y_warmup
                            gc.collect()
                        
                        # Now perform the actual benchmark iterations
                        differences = []
                        for _ in tqdm(range(iterations), 
                                    desc="Benchmarking", 
                                    leave=False, 
                                    disable=iterations < 5):  # Only show if >= 5 iterations
                            x, y = input_handler_instance.get_from_file(**params)
                            if len(x) != len(y):
                                raise ValueError(
                                    f"Length mismatch! {option=}, {file_input=}, {n_size=}, len(x)={len(x)}, len(y)={len(y)}"
                                )
                            differences.append(experiment_fn(x, y, option))
                            del x
                            del y

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
                            "iterations": iterations,
                            "measurement_unit": measurement_unit,
                            "n_out": n_out
                        }

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
                    
                    finally:
                        pbar.update(1)  # Update main progress bar
                    
    return results


def get_x_column_from_file(file_path):
    """
    Get the column index for the x values based on the file path.
    """
    return map_file_to_x_column.get(file_path, 0)  # Default to 0 if not found

def get_y_column_from_file(file_path):
    """
    Get the column index for the y values based on the file path.
    """
    return map_file_to_y_column.get(file_path, COLUMN)  # Default to 1 if not found

def get_decimal_places_from_file(file_path):
    """
    Get the number of decimal places based on the file path.
    """
    return map_file_to_decimal_places.get(file_path, DECIMAL_PLACES) 
