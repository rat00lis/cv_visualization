import compressed_vector as cv
import csv

class InputHandler:
    def __init__(self):
        self.valid_input_types = ["default", "sdsl4py"]
        self.width_y = 64
        self.width_x = 64

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
        
    def get_from_file(self, file_path, option, decimal_places=2, delimiter=";", column=1, truncate=None, decompressed=False):
        """
            Read data from a file and return two lists of integers.
            Args:
                file_path (str): The path to the file.
                option (str): The input type, either "default" or "sdsl4py".
                decimal_places (int): The number of decimal places to round to.
                delimiter (str): The delimiter used in the file.
                column (int): The column to read from the file.
                truncate (int): If specified, truncate the lists to this length.
                decompressed (bool): If True, return decompressed vectors.
            Returns:
                tuple: Two lists of integers either as CompressedVector or regular lists.
        """
        x = []
        y = []
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
            
            case "sdsl4py":
                # create the compressed vector
                compressed_vector_instance_x = cv.CompressedVector(decimal_places, self.width_x)
                compressed_vector_instance_x.create_vector(len(x))
                compressed_vector_instance_x.fill_from_vector(x)
                compressed_vector_instance_x.set_decompressed_config(decompressed)
                compressed_vector_instance_y = cv.CompressedVector(decimal_places, self.width_y)
                compressed_vector_instance_y.create_vector(len(y))
                compressed_vector_instance_y.fill_from_vector(y)
                compressed_vector_instance_y.set_decompressed_config(decompressed)

                return compressed_vector_instance_x, compressed_vector_instance_y