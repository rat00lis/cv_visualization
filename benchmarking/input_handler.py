import csv
from cv_visualization import CompressedVectorDownsampler as cvd
from cv_visualization import CompressedVector as cv
from cv_visualization import DOWNSAMPLERS, COMPRESSION_METHODS
import tsdownsample as tsd
import sdsl4py as sdsl
import numpy as np

class InputHandler:
    def __init__(self):
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
            
    def get_from_file(self, file_path, option, decimal_places=2, delimiter=";", column=1, truncate=None, decompressed=False, compress_option=None, n_out=None, downsampler=tsd.MinMaxLTTBDownsampler, x_column = 0):
        """
            Read data from a file and return two lists of integers or compressed vectors.
        """
        x, y = [], []

        # Auto-detect delimiter for CSV files
        if file_path.endswith('.csv'):
            delimiter = ','
        
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file, delimiter=delimiter)
                row_count = 0
                valid_rows = 0
                
                for i, row in enumerate(reader):
                    row_count += 1
                    
                    # Skip header
                    if i == 0:
                        continue
                        
                    if truncate is not None and i >= truncate:
                        break
                        
                    # Check if row has enough columns
                    if len(row) <= max(column, x_column):
                        continue
                    
                    try:
                        # Handle x-column (might be date or numeric)
                        x_val = self._parse_value(row[x_column], is_x_axis=True)
                        # Handle y-column (should be numeric)
                        y_val = float(row[column])
                        
                        x.append(x_val)
                        y.append(y_val)
                        valid_rows += 1
                        
                    except (ValueError, IndexError) as e:
                        if valid_rows < 10:  # Only print first few errors to avoid spam
                            print(f"⚠️ Could not parse row {i}: {row[:5]}... Error: {e}")
                        continue
                
                
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return [], []
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return [], []

        # Handle empty data
        if len(x) == 0 or len(y) == 0:
            exception = ValueError("No valid data found in the file, make sure the file is not empty and that you consider the header of the file.")
            raise exception
        
        if option == "default":
            return x, y
        elif option == "compressed_vector":
            cx = self.compress_vector(x, decimal_places, self.width_x, decompressed, compress_option)
            cy = self.compress_vector(y, decimal_places, self.width_y, decompressed, compress_option)
            return cx, cy
        elif option == "compressed_vector_downsampler":
            if file_path == "./benchmarking/input/yellow_tripdata_2015-01.csv":
                self.y_width = 8
            # Validate n_out before calling downsample
            if n_out and n_out >= len(x):
                n_out = max(1, len(x)//2)
                
            cv_downsampler = cvd()
            cx, cy = cv_downsampler.downsample(
                y=y,
                x=x,
                n_out=n_out,
                method=downsampler,
                int_width=self.width_x,
                decimal_places=decimal_places,
                compress_method=compress_option,
                y_width = self.width_y
            )
            self.x_indices = cv_downsampler.get_x_indices()
            self.y_indices = cv_downsampler.get_y_indices()
            return cx, cy
        elif option == "tsdownsample":
            # Validate n_out for tsdownsample as well
            if n_out and n_out >= len(y):
                # n_out = max(1, len(y)//2)
                #throw error
                raise ValueError("n_out must be less than the length of the data")
                
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
        
        elif option == "sdsl4py":
            compress_fn = COMPRESSION_METHODS.get(compress_option, None)
            if self.width_x == 8:
                x_vector = sdsl.int_vector_8(len(x), default_value=0)
                y_vector = sdsl.int_vector_8(len(y), default_value=0)
            elif self.width_x == 16:
                x_vector = sdsl.int_vector_16(len(x), default_value=0)
                y_vector = sdsl.int_vector_16(len(y), default_value=0)
            elif self.width_x == 32:
                x_vector = sdsl.int_vector_32(len(x), default_value=0)
                y_vector = sdsl.int_vector_32(len(y), default_value=0)
            elif self.width_x == 64:
                x_vector = sdsl.int_vector_64(len(x), default_value=0)
                y_vector = sdsl.int_vector_64(len(y), default_value=0)
            else:
                raise ValueError("Invalid self.width_x for SDSL4Py vector")
            
            for i in range(len(x)):
                x_vector[i] = abs(int(x[i]))
            for i in range(len(y)):
                y_vector[i] = abs(int(y[i]))
                
            if compress_fn is None:
                return x_vector, y_vector
            
            if compress_fn is not None:
                compressed_x = compress_fn(x_vector)
                compressed_y = compress_fn(y_vector)
                
            return compressed_x, compressed_y
        
        else:
            raise ValueError(f"Unknown option: {option}")

    def _parse_value(self, value, is_x_axis=False):
        """
        Parse a value that could be a number or a date string.
        """
        # First try to parse as float
        try:
            return float(value)
        except ValueError:
            pass
        
        # If that fails and it looks like a date, convert to timestamp
        try:
            from datetime import datetime
            # Try common date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y']:
                try:
                    date_obj = datetime.strptime(value, fmt)
                    return date_obj.timestamp()
                except ValueError:
                    continue
            
            # If no format worked, raise an error
            raise ValueError(f"Could not parse '{value}' as number or date")
            
        except Exception as e:
            raise ValueError(f"Could not parse '{value}': {e}")



                
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

    def convert_string_date_to_unix(self, date_str):
        """
        Convert a date string to a Unix timestamp.
        
        :param date_str: The date string to convert.
        :return: The Unix timestamp as an integer.
        """
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
