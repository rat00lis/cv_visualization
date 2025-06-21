import sdsl4py
import math
import numpy as np

class CompressedVector:
    def __init__(
        self,
        decimal_places=0,
        int_width=64,
        dtype=float,
        get_decompressed = True
    ):
        """
        Initialize the CompressedVector with default values.
        Args:
            decimal_places (int): Number of decimal places to keep.
            int_width (int): Width of the integer part in bits. (default: 64)
        """
        if decimal_places < 0:
            raise ValueError("Decimal places must be non-negative")
        if decimal_places > int_width:
            raise ValueError("Decimal places cannot be greater than int_width")
        
        self.decimal_places = decimal_places
        self.int_width = int_width
        self.current = 0
        self.n_elements = 0
        self.get_decompressed = get_decompressed

    
    @property
    def dtype(self):
        """
        Return the data type of the compressed vector.
        """
        return np.dtype(float)
    
    @property
    def ndim(self):
        return 1

    @property
    def shape(self):
        return (self.n_elements,)
    
    @property
    def size(self):
        return self.n_elements


    def __iter__(self):
        """
        Initialize the iterator for the CompressedVector.
        Returns:
            self: The CompressedVector instance itself for iteration.
        """
        self.current = 0  # Reset the current index for iteration
        return self
    
    def __next__(self):
        """
        Return the next value in the compressed vector.
        Returns:
            float: The next value in the compressed vector, reconstructed from the integer and decimal parts.
        """
        if self.current < self.n_elements:
            value = self._reconstruct_float_value(self.current)
            self.current += 1
            return value
        raise StopIteration

    def __len__(self):
        """
        Return the number of elements in the compressed vector.
        """
        return self.n_elements
    
    def __getitem__(self, index):
        """
        Get the value at the given index or a slice of values.
        Args:
            index (int, slice, list, np.ndarray, tuple): The index or slice to retrieve values from.
        Returns:
            if the flag get_decompressed is True, returns a numpy array of float values.
            if the flag get_decompressed is False, returns a new CompressedVector with the specified indices.
        """
        if isinstance(index, int):
            # Handle negative indices like native Python lists
            if index < 0:
                index += self.n_elements
            if index < 0 or index >= self.n_elements:
                raise IndexError("Index out of bounds")
            return self._reconstruct_float_value(index)

        elif isinstance(index, (slice, list, np.ndarray, tuple)):
            # when index is a slice, list, ndarray or tuple and
            # get_decompressed is True, return a numpy array of float values
            if self.get_decompressed:
                if isinstance(index, slice):
                    # Convert slice to a proper list of indices
                    index = range(*index.indices(self.n_elements))

                selected = np.array(index)
                int_arr = np.asarray(self.integer_part)
                dec_arr = np.asarray(self.decimal_part)
                sign_arr = np.asarray(self.sign_part)

                denom = 10 ** self.decimal_places
                float_arr = int_arr[selected] + dec_arr[selected] / denom
                float_arr[sign_arr[selected] == 0] *= -1
                return float_arr
            
            # else if get_decompressed is False, return a new CompressedVector
            else:
                new_vector = CompressedVector(
                    decimal_places=self.decimal_places,
                    int_width=self.int_width,
                    get_decompressed=False
                )

                if isinstance(index, slice):
                    start, stop, step = index.indices(self.n_elements)
                    index_range = range(start, stop, step)
                    len_index = len(index_range)
                    new_vector.create_vector(len_index)
                    new_vector.fill_from_vector(self, start=start, end=stop)
                else:
                    len_index = len(index)
                    new_vector.create_vector(len_index)
                    new_vector.fill_from_vector(self, start=0, end=len_index)

                return new_vector

        else:
            raise TypeError(f"Invalid index type: {type(index)}. Expected int, slice, list or ndarray.")


    def __setitem__(self, index, value):
        """
        Set the value at the given index.
        Args:
            index (int): The index to set the value at.
            value (float): The value to set.
        """
        # Handle set the value at the specified index
        if isinstance(index, int):
            if index < 0 or index >= self.n_elements:
                raise IndexError("Index out of range")
            
            self._insert_value(index, value)


    def _insert_value(self, index, value):
        """
        Insert a value at the specified index.
        Args:
            index (int): The index to insert the value at.
            value (float): The value to insert.
        """
        # Check for NaN values
        if math.isnan(value):
            self.integer_part[index] = 0
            self.decimal_part[index] = 0
            self.sign_part[index] = 2  # Special code for NaN (not 0 or 1)
            return
            
        from decimal import Decimal

        value_dec = Decimal(str(abs(value)))
        int_part = int(value_dec)
        dec_part = value_dec - int_part
        dec_part = round(dec_part, self.decimal_places)
        dec_part = int(dec_part * (10 ** self.decimal_places))
        sign_part = 1 if value >= 0 else 0
        self.integer_part[index] = int_part
        self.decimal_part[index] = dec_part
        self.sign_part[index] = sign_part

    def _create_vector(self, vector_type):
        """
        Create the integer and decimal vectors with the specified type.
        """
        self.integer_part = vector_type(size=self.n_elements, default_value=0)
        self.decimal_part = vector_type(size=self.n_elements, default_value=0)
        self.sign_part = vector_type(size=self.n_elements, default_value=0)

    def _reconstruct_float_value(self, index):
        """
        Reconstructs the original float value at the given index by combining
        integer part, decimal part and sign.

        Args:
            index (int): Index of the value to reconstruct

        Returns:
            float: Reconstructed value with correct sign
        """
        from decimal import Decimal
        
        if self.sign_part[index] == 2:
            return float('nan')
            
        int_part = Decimal(self.integer_part[index])
        dec_part = Decimal(self.decimal_part[index]) / (Decimal(10) ** self.decimal_places)
        value = int_part + dec_part
        return float(value if self.sign_part[index] == 1 else -value)
    
    def set_decompressed_config(self, get_decompressed):
        """
        Set the configuration for decompression.
        Args:
            get_decompressed (bool): Whether to return decompressed values.
        """
        self.get_decompressed = get_decompressed

    def create_vector(self, size):
        """
        Create the integer and decimal vectors.
        """
        self.n_elements = size
        match self.int_width:
            case 8:
                self._create_vector(sdsl4py.int_vector_8)
            case 16:
                self._create_vector(sdsl4py.int_vector_16)
            case 32:
                self._create_vector(sdsl4py.int_vector_32)
            case 64:
                self._create_vector(sdsl4py.int_vector_64)
            case _:
                print(f"Unsupported int_width: {self.int_width}, defaulting to 64")
                self._create_vector(sdsl4py.int_vector_64)

    
    def fill_from_vector(self, original_vector, start=0, end=None):
        """
        Build the compressed vector from a vector.
        Args:
            original_vector (list): The original vector to fill the compressed vector with.
            start (int): The start index in the original vector (inclusive).
            end (int): The end index in the original vector (exclusive). If None, use the length of the vector.
        """
        if self.integer_part is None or self.decimal_part is None or self.sign_part is None:
            raise ValueError("Vectors not created. Call create_vector() first.")
        
        # Handle default end value and validate indices
        if end is None:
            end = len(original_vector)
        elif end > len(original_vector):
            end = len(original_vector)
        
        # Ensure start is valid
        start = max(0, start)
        
        for i in range(start, end):
            self.current += 1
            self._insert_value(self.current - 1, original_vector[i])
                
        self.n_elements = (end - start)
        self.current = 0

    def fill_from_file(self, file_path, column=1, delimiter=";", truncate=None):
        """
        Build the compressed vector from a specific column in a csv file.
        Args:
            file_path (str): The path to the file containing the original vector.
            column (int): The column index (0-based) to extract the vector from.
            delimiter (str): The delimiter used in the csv file.
            truncate (int): The maximum number of rows to process. If None, process all rows.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()
            original_vector = []
            for i, line in enumerate(lines):
                if truncate is not None and i >= truncate:
                    break
                values = line.strip().split(delimiter)
                if len(values) > column:
                    value_to_add = values[column]
                    try:
                        value_to_add = float(value_to_add)
                        self.current += 1
                        self._insert_value(self.current-1, value_to_add)
                    except ValueError:
                        print(f"Invalid value at line {i}: {value_to_add}")
                    
            self.n_elements = len(original_vector)
            self.current = 0
    
    def size_in_bytes(self):
        """
        Return the size in bytes of the compressed vector.
        Returns:
            int: Total size in bytes of the compressed vector.
        Raises:
            ValueError: If the vector components are not initialized.
        """
        if self.integer_part is None or self.decimal_part is None or self.sign_part is None:
            raise ValueError("You called size_in_bytes without creating the vectors or after destroying them. Call create_vector() first.")
            
        total = (
                # sdsl4py vectors
                sdsl4py.size_in_bytes(self.integer_part) 
                + sdsl4py.size_in_bytes(self.decimal_part)
                + sdsl4py.size_in_bytes(self.sign_part)
                )
        return total
    
    def compress(self, vector_type=sdsl4py.int_vector_64):
        """
        Compress the vector using the specified vector type.
        Args:
            vector_type: The type of vector to use for compression.
        """
        if self.integer_part is None or self.decimal_part is None or self.sign_part is None:
            raise ValueError("Vectors not created. Call create_vector() first.")
        
        # Create compressed vectors
        self.integer_part = vector_type(self.integer_part)
        self.decimal_part = vector_type(self.decimal_part)
        self.sign_part = vector_type(self.sign_part)

    def destroy(self):
        """
        Destroy the compressed vector and free memory.
        """
        if self.integer_part is not None:
            del self.integer_part
            self.integer_part = None
        if self.decimal_part is not None:
            del self.decimal_part
            self.decimal_part = None
        if self.sign_part is not None:
            del self.sign_part
            self.sign_part = None
        
        # Reset attributes
        self.n_elements = 0
        self.current = 0
        self.decimal_places = 0