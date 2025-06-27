from compressed_vector import CompressedVector
import sdsl4py

import tsdownsample as tsd
import numpy as np


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


class CompressedVectorDownsampler:
    def __init__(self):
        self.x_indices = None
        self.y_indices = None
        return

    def downsample(
        self,
        y=None,
        x=None,
        n_out=1000,
        method="MinMaxLTTBDownsampler",
        int_width=64,
        decimal_places=4,
        compress_method="vlc_vector_fibonacci"):
        """
        Downsample a time series using the specified method and compress the result.

        :param y: Y-axis values of the time series (can be None if x is provided).
        :param x: X-axis values (optional, used for irregularly spaced data).
        :param n_out: Target number of downsampled points.
        :param method: Downsampling method to use (name or instance).
        :param int_width: Bit width of integers in compressed vector.
        :param decimal_places: Number of decimal places for float precision.
        :param compress_method: Compression method to apply (name or function).
        :return: One or two CompressedVector instances depending on input.
        """
        if x is None and y is None:
            raise ValueError("At least one of 'x' or 'y' must be provided for downsampling.")

        downsampler = self._select_downsampler(method)

        # Downsample based on inputs
        if x is not None and y is not None:
            indices = downsampler.downsample(x, y, n_out=n_out)
        elif y is not None:
            indices = downsampler.downsample(y, n_out=n_out)
        else:
            indices = downsampler.downsample(x, n_out=n_out)

        compress_method_selected = self._select_compression_method(compress_method)

        result = {}
        
        self.x_indices = indices if x is not None else None
        self.y_indices = indices if y is not None else None
        
        if x is not None:
            cv_x = CompressedVector(
                int_width=int_width,
                decimal_places=decimal_places,
                get_decompressed=False
            )
            cv_x.create_vector(len(indices))
            # Convert x to numpy array if it's a list to support fancy indexing
            x_array = np.array(x) if not isinstance(x, np.ndarray) else x
            cv_x.fill_from_vector(x_array[indices])
            if compress_method_selected is not None:
                cv_x.compress(compress_method_selected)
            result["x"] = cv_x

        if y is not None:
            cv_y = CompressedVector(
                int_width=int_width,
                decimal_places=decimal_places,
                get_decompressed=False
            )
            cv_y.create_vector(len(indices))
            # Convert y to numpy array if it's a list to support fancy indexing
            y_array = np.array(y) if not isinstance(y, np.ndarray) else y
            cv_y.fill_from_vector(y_array[indices])
            if compress_method_selected is not None:
                cv_y.compress(compress_method_selected)
            result["y"] = cv_y

        # Return only what's available
        if "x" in result and "y" in result:
            return result["x"], result["y"]
        elif "y" in result:
            return result["y"]
        else:
            return result["x"]


    def get_x_indices(self):
        """
        Get the x indices used in the last downsampling operation.
        
        :return: CompressedVector containing x indices or None if not available.
        """
        return self.x_indices
    
    def get_y_indices(self):
        """
        Get the y indices used in the last downsampling operation.
        
        :return: CompressedVector containing y indices or None if not available.
        """
        return self.y_indices
    
    def set_get_decompressed(self, get_decompressed):
        """
        Set whether the CompressedVector should return decompressed values.
        
        :param get_decompressed: Boolean indicating whether to return decompressed values.
        """
        if not isinstance(get_decompressed, bool):
            raise TypeError("get_decompressed must be a boolean value.")
        CompressedVector.set_decompressed_config(get_decompressed)

    def _select_downsampler(self, downsampler):
        if hasattr(downsampler, 'downsample'):  # Ya es una instancia
            return downsampler
        if isinstance(downsampler, str):
            try:
                return DOWNSAMPLERS[downsampler]()  # Instanciar
            except KeyError:
                raise ValueError(
                    f"Unknown downsampling method: '{downsampler}'. "
                    f"Available: {', '.join(DOWNSAMPLERS)}"
                )
        raise TypeError("downsampler must be a string or a downsampler instance.")
    
    def _select_compression_method(self, method):
        if method in COMPRESSION_METHODS.values() or method is None:
            return method
        if isinstance(method, str):
            try:
                return COMPRESSION_METHODS[method]
            except KeyError:
                raise ValueError(
                    f"Unknown compression method: '{method}'. "
                    f"Available: {', '.join(COMPRESSION_METHODS)}"
                )
        raise TypeError("compression method must be a string or a valid function.")
    
    def list_available_downsamplers():
        return list(DOWNSAMPLERS.keys())

    def list_available_compression_methods():
        return list(COMPRESSION_METHODS.keys())
