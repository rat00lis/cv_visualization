import csv
from cv_visualization import CompressedVectorDownsampler as cvd
from cv_visualization import CompressedVector as cv
from cv_visualization import DOWNSAMPLERS, COMPRESSION_METHODS
import tsdownsample as tsd
import numpy as np

class InputHandler:
    def __init__(self):
        self.valid_input_types = ["default", "sdsl4py"]
        self.width_y = 64
        self.width_x = 64
        self.x_indices = None
        self.y_indices = None

    def set_width(self, width, option):
        """
            Set the width of the integer part in bits.
            Args:
                width (int): The width of the integer part in bits. Only 8, 16, 32, or 64 are valid.
                axis (str): The axis to set the width for. Can be "x" or "y".
        """
        if option == "y":
            if width not in [8, 16, 32, 64]:
                raise ValueError("Width must be one of [8, 16, 32, 64]")
            self.width_y = width
        elif option == "x":
            if width not in [8, 16, 32, 64]:
                raise ValueError("Width must be one of [8, 16, 32, 64]")
            self.width_x = width
        else:
            raise ValueError("Option must be 'x' or 'y'")
            
    def get_from_file(self, file_path, option, decimal_places=2, delimiter=";", column=1, truncate=None, decompressed=False, compress_option=None, n_out=None, downsampler=tsd.MinMaxLTTBDownsampler):
        """
            Read data from a file and return two lists of integers or compressed vectors.
            Args:
                file_path (str): The path to the file.
                option (str): The input type, either "default" or "sdsl4py".
                decimal_places (int): The number of decimal places to round to.
                delimiter (str): The delimiter used in the file.
                column (int): The column to read from the file.
                truncate (int): If specified, truncate the lists to this length.
                decompressed (bool): If True, return decompressed vectors.
                compress_option (str): Name of the compression method to apply.
            Returns:
                tuple: Two vectors as raw lists or CompressedVector instances.
        """
        x, y = [], []

        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter=delimiter)
            for i, row in enumerate(reader):
                if truncate is not None and i >= truncate:
                    break
                if len(row) > column:
                    x.append(float(row[0]))
                    y.append(float(row[column]))

        match option:
            case "default":
                return x, y

            case "compressed_vector":
                cx = self.compress_vector(x, decimal_places, self.width_x, decompressed, compress_option)
                cy = self.compress_vector(y, decimal_places, self.width_y, decompressed, compress_option)
                return cx, cy
            
            case "compressed_vector_downsampler":
                cv_downsampler = cvd()
                cx, cy = cv_downsampler.downsample(
                    y=y,
                    x=x,
                    n_out=n_out,
                    method=downsampler,
                    int_width=self.width_x,
                    decimal_places=decimal_places,
                    compress_method=compress_option
                )
                self.x_indices = cv_downsampler.get_x_indices()
                self.y_indices = cv_downsampler.get_y_indices()
                return cx, cy
            
            case "tsdownsample":
                ds = downsampler()
                if x is not None and not isinstance(ds, tsd.EveryNthDownsampler):
                    indices = ds.downsample(x, y, n_out=n_out)
                else:
                    indices = ds.downsample(y, n_out=n_out)

                indices = np.asarray(indices, dtype=np.int64)
                x = np.asarray(x, dtype=np.float64) if x is not None else None
                y = np.asarray(y, dtype=np.float64) if y is not None else None
                self.x_indices = indices if x is not None else None
                self.y_indices = indices if y is not None else None
                return x[indices] if x is not None else None, y[indices]



                
    def compress_vector(self, data, decimal_places, bit_width, decompressed=False, compress_option=None):
        vec = cv(decimal_places, bit_width)
        vec.create_vector(len(data))
        vec.fill_from_vector(data)
        vec.set_decompressed_config(decompressed)
        if compress_option is not None and compress_option != "No Compression":
            compress_method = COMPRESSION_METHODS.get(compress_option, None)
            if compress_method is None:
                raise ValueError(f"Unknown compression method: {compress_option}")
            vec.compress(compress_method)
        return vec

    def get_x_indices(self):
        """
        Get the x indices used in the last operation.
        
        :return: CompressedVector containing x indices or None if not available.
        """
        return self.x_indices
    
    def get_y_indices(self):
        """
        Get the y indices used in the last operation.
        
        :return: CompressedVector containing y indices or None if not available.
        """
        return self.y_indices
