from compressed_vector_downsampler.available_methods import DOWNSAMPLERS, COMPRESSION_METHODS
from common import get_original_vector_and_decimal_places_with_file, verify_compressed_vector, verify_not_compressed_vector
from benchmarking.input_handler import InputHandler as ih
import numpy as np
import pytest

INT_WIDTH = 64
INPUT_PATH = "integration_tests/test_input/test.txt"

all_methods = list(DOWNSAMPLERS.keys())
all_compression_methods = list(COMPRESSION_METHODS.keys())


def test_input_handler_default():
    original_vector, decimal_places = get_original_vector_and_decimal_places_with_file(INPUT_PATH, INT_WIDTH)
    original_vector = np.asarray(original_vector, dtype=np.float64)
    input_handler = ih()
    x, y = input_handler.get_from_file(
        file_path=INPUT_PATH,
        option="default",
        decimal_places=decimal_places,
        compress_option=None,
        n_out=1000
    )

    verify_not_compressed_vector(
        original_vector=original_vector,
        decimal_places=decimal_places,
        compressed_vector=y
    )


def test_input_handler_compressed_vector():
    original_vector, decimal_places = get_original_vector_and_decimal_places_with_file(INPUT_PATH, INT_WIDTH)
    original_vector = np.asarray(original_vector, dtype=np.float64)
    input_handler = ih()
    x, y = input_handler.get_from_file(
        file_path=INPUT_PATH,
        option="compressed_vector",
        decimal_places=decimal_places,
        compress_option=None,
        n_out=1000
    )

    verify_compressed_vector(
        original_vector=original_vector,
        decimal_places=decimal_places,
        compressed_vector=y
    )


@pytest.mark.parametrize("ts_method", all_methods)
def test_compressed_vector_tsdownsampler(ts_method):
    original_vector, decimal_places = get_original_vector_and_decimal_places_with_file(INPUT_PATH, INT_WIDTH)
    original_vector = np.asarray(original_vector, dtype=np.float64).flatten()

    input_handler = ih()
    x, y = input_handler.get_from_file(
        file_path=INPUT_PATH,
        option="tsdownsample",
        decimal_places=decimal_places,
        n_out=1000,
        downsampler=DOWNSAMPLERS[ts_method]
    )
    x_indices = input_handler.get_x_indices()
    y_indices = input_handler.get_y_indices()

    verify_not_compressed_vector(
        original_vector=original_vector[y_indices],
        decimal_places=decimal_places,
        compressed_vector=y
    )


@pytest.mark.parametrize("ts_method", all_methods)
@pytest.mark.parametrize("compress_method", all_compression_methods)
def test_compressed_vector_downsampler(ts_method, compress_method):
    original_vector, decimal_places = get_original_vector_and_decimal_places_with_file(INPUT_PATH, INT_WIDTH)
    original_vector = np.asarray(original_vector, dtype=np.float64)

    input_handler = ih()
    x, y = input_handler.get_from_file(
        file_path=INPUT_PATH,
        option="compressed_vector_downsampler",
        decimal_places=decimal_places,
        n_out=1000,
        downsampler=DOWNSAMPLERS[ts_method],
        compress_option=compress_method
    )

    y_indices = input_handler.get_y_indices()
    verify_not_compressed_vector(
        original_vector=original_vector[y_indices],
        decimal_places=decimal_places,
        compressed_vector=y
    )
