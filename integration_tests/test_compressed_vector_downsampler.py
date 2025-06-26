from compressed_vector_downsampler import CompressedVectorDownsampler as cvd
from common import get_original_vector_and_decimal_places, verify_compressed_vector
import numpy as np

INT_WIDTH = 64

all_methods = [
    "EveryNthDownsampler",
    "LTTBDownsampler",
    "M4Downsampler",
    "MinMaxDownsampler",
    "MinMaxLTTBDownsampler",
    "NaNM4Downsampler",
    "NaNMinMaxDownsampler",
    "NaNMinMaxLTTBDownsampler",
]
all_compression_methods = [
    "enc_vector_elias_gamma",
    "enc_vector_fibonacci",
    "enc_vector_comma_2",
    "enc_vector_elias_delta",
    "vlc_vector_elias_delta",
    "vlc_vector_elias_gamma",
    "vlc_vector_fibonacci",
    "vlc_vector_comma_2",
    "No Compression",
]

def test_compressed_vector_downsampler_MinMaxLTTBDownsampler():
    for ts_method in all_methods:
        for cvd_method in all_compression_methods:
            original_vector, decimal_places = get_original_vector_and_decimal_places(INT_WIDTH)
            original_vector = np.asarray(original_vector, dtype=np.float64)
            cv_downsampler = cvd()
            downsampled_y = cv_downsampler.downsample(
                y=original_vector,
                n_out=1000,
                method=ts_method,
                int_width=INT_WIDTH,
                decimal_places=decimal_places,
                compress_method=cvd_method
            )
            y_indices = cv_downsampler.get_y_indices()
            verify_compressed_vector(
                original_vector=original_vector[y_indices],
                decimal_places=decimal_places,
                compressed_vector=downsampled_y
            )
