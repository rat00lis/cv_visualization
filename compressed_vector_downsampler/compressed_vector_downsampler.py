from compressed_vector import CompressedVector
import tsdownsample
import sdsl4py

import tsdownsample as tsd
import numpy as np

class CompressedVectorDownsampler:
    def __init__(self):
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

        if x is not None:
            cv_x = CompressedVector(
                int_width=int_width,
                decimal_places=decimal_places,
                get_decompressed=False
            )
            cv_x.create_vector(len(indices))
            cv_x.fill_from_vector(x[indices])
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
            cv_y.fill_from_vector(y[indices])
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



    def set_get_decompressed(self, get_decompressed):
        """
        Set whether the CompressedVector should return decompressed values.
        
        :param get_decompressed: Boolean indicating whether to return decompressed values.
        """
        if not isinstance(get_decompressed, bool):
            raise TypeError("get_decompressed must be a boolean value.")
        CompressedVector.set_decompressed_config(get_decompressed)

    def _select_compression_method(self, method):
        """
        Resolves the compression method from a string or directly returns the function if already valid.
        
        :param method: Either a string with the method name or a compression function (or None).
        :return: A function or None (for "No Compression").
        """
        known_methods = {
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

        if method in known_methods.values() or method is None:
            return method

        if isinstance(method, str):
            if method in known_methods:
                return known_methods[method]
            else:
                raise ValueError(
                    f"Unknown compression method: '{method}'. "
                    f"Available methods are: {', '.join(known_methods.keys())}"
                )

        raise TypeError("method must be either a string or a valid compression function")


    def _select_downsampler(self, downsampler):
        """
        Returns the appropriate downsampler instance.
        If `downsampler` is an instance of a known downsampler, return it as is.
        If it's a string, instantiate and return the corresponding downsampler.

        :param downsampler: Either a string with the name of the method or a downsampler instance.
        :return: A downsampler instance.
        """
        known_classes = (
            tsd.EveryNthDownsampler,
            tsd.LTTBDownsampler,
            tsd.M4Downsampler,
            tsd.MinMaxDownsampler,
            tsd.MinMaxLTTBDownsampler,
            tsd.NaNM4Downsampler,
            tsd.NaNMinMaxDownsampler,
            tsd.NaNMinMaxLTTBDownsampler,
        )

        if isinstance(downsampler, known_classes):
            return downsampler

        if isinstance(downsampler, str):
            match downsampler:
                case "MinMaxLTTBDownsampler":
                    return tsd.MinMaxLTTBDownsampler()
                case "M4Downsampler":
                    return tsd.M4Downsampler()
                case "LTTBDownsampler":
                    return tsd.LTTBDownsampler()
                case "MinMaxDownsampler":
                    return tsd.MinMaxDownsampler()
                case "EveryNthDownsampler":
                    return tsd.EveryNthDownsampler()
                case "NaNM4Downsampler":
                    return tsd.NaNM4Downsampler()
                case "NaNMinMaxDownsampler":
                    return tsd.NaNMinMaxDownsampler()
                case "NaNMinMaxLTTBDownsampler":
                    return tsd.NaNMinMaxLTTBDownsampler()
                case _:
                    raise ValueError(
                        f"Unknown downsampling method: '{downsampler}'. "
                        "Available methods are: "
                        "MinMaxLTTBDownsampler, M4Downsampler, LTTBDownsampler, "
                        "MinMaxDownsampler, EveryNthDownsampler, NaNM4Downsampler, "
                        "NaNMinMaxDownsampler, NaNMinMaxLTTBDownsampler"
                    )

        raise TypeError("downsampler must be either a string or a downsampler instance")
