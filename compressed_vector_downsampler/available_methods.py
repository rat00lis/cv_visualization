import tsdownsample as tsd
import sdsl4py

DOWNSAMPLERS = {
    "MinMaxLTTBDownsampler": tsd.MinMaxLTTBDownsampler,
    "M4Downsampler": tsd.M4Downsampler,
    "LTTBDownsampler": tsd.LTTBDownsampler,
    "MinMaxDownsampler": tsd.MinMaxDownsampler,
    "EveryNthDownsampler": tsd.EveryNthDownsampler,
    "NaNM4Downsampler": tsd.NaNM4Downsampler,
    "NaNMinMaxDownsampler": tsd.NaNMinMaxDownsampler,
    "NaNMinMaxLTTBDownsampler": tsd.NaNMinMaxLTTBDownsampler,
}

COMPRESSION_METHODS = {
    "enc_vector_elias_gamma": sdsl4py.enc_vector_elias_gamma,
    "enc_vector_fibonacci": sdsl4py.enc_vector_fibonacci,
    "enc_vector_comma_2": sdsl4py.enc_vector_comma_2,
    "enc_vector_elias_delta": sdsl4py.enc_vector_elias_delta,
    "vlc_vector_elias_delta": sdsl4py.vlc_vector_elias_delta,
    "vlc_vector_elias_gamma": sdsl4py.vlc_vector_elias_gamma,
    "vlc_vector_fibonacci": sdsl4py.vlc_vector_fibonacci,
    "vlc_vector_comma_2": sdsl4py.vlc_vector_comma_2,
    "No Compression": None,
}

def list_available_downsamplers():
    return list(DOWNSAMPLERS.keys())

def list_available_compression_methods():
    return list(COMPRESSION_METHODS.keys())
