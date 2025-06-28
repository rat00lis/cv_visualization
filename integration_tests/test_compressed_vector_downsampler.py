import pytest
import numpy as np

from cv_visualization import CompressedVectorDownsampler as cvd
from cv_visualization import DOWNSAMPLERS, COMPRESSION_METHODS
from utils import get_original_vector_and_decimal_places, verify_compressed_vector

INT_WIDTH = 64

all_methods = list(DOWNSAMPLERS.keys())
all_compression_methods = list(COMPRESSION_METHODS.keys())

@pytest.mark.parametrize("ts_method", all_methods)
@pytest.mark.parametrize("compress_method", all_compression_methods)
def test_compressed_vector_downsampler(ts_method, compress_method):
    original_vector, decimal_places = get_original_vector_and_decimal_places(INT_WIDTH)
    original_vector = np.asarray(original_vector, dtype=np.float64)

    cv_downsampler = cvd()
    downsampled_y = cv_downsampler.downsample(
        y=original_vector,
        n_out=1000,
        method=ts_method,
        int_width=INT_WIDTH,
        decimal_places=decimal_places,
        compress_method=compress_method
    )

    y_indices = cv_downsampler.get_y_indices()
    verify_compressed_vector(
        original_vector=original_vector[y_indices],
        decimal_places=decimal_places,
        compressed_vector=downsampled_y
    )
