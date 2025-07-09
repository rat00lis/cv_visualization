NUM_ITERATIONS = 100
N_OUT = 1000  # Number of output points for downsampling
ROOT_OUTPUT_FOLDER = "./benchmarking/output/"
N_RANGE = range(10000, 350000, 20000)
DECIMAL_PLACES = 4
DELIMITER = ";"
COLUMN = 1
DECOMPRESSED = False  # Whether to use decompressed subvectors
WIDTH = 64  # 16 bits can represent numbers from 0 to 65535, enough for 4-digit numbers
FILE_INPUT_LIST = [
    "./benchmarking/input/dataset_bridge/d_08_1_1_1.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_2.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_3.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_4.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_5.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_6.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_7.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_8.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_9.txt",
    "./benchmarking/input/dataset_bridge/d_08_1_1_10.txt"
]
MEASUREMENT_UNIT = "seconds"  # Default measurement unit for time-based experiments

def add_base_config(exp):
    """
    Add the base configuration for the experiment.
    """
    exp.add_config({
        "iterations": NUM_ITERATIONS,
        "n_range": N_RANGE,
        "output_folder": ROOT_OUTPUT_FOLDER,
        "decimal_places": DECIMAL_PLACES,
        "delimiter": DELIMITER,
        "column": COLUMN,
        "file_input_list": FILE_INPUT_LIST,
        "width": WIDTH,
        "decompressed": DECOMPRESSED,
        "measurement_unit": MEASUREMENT_UNIT,
        "n_out": N_OUT
    })

