from benchmarking.exp_runner import setup_experiment, run_with_timing
from benchmarking.input_handler import InputHandler
from cv_visualization import COMPRESSION_METHODS, DOWNSAMPLERS, CompressedVector
import numpy as np
import pandas as pd
import sys
exp_name = "Space Used By Decimal Places"
exp = setup_experiment(exp_name)


@exp.config
def default_config():



@exp.automain
def run(cases, iterations, n_range, file_input_list, decimal_places, width, decompressed, measurement_unit, n_out):
