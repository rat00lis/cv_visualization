import numpy as np
from cv_visualization import CompressedVector
from utils import get_original_vector_and_decimal_places, verify_compressed_vector
import sdsl4py

def test_int_vector_64():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)
    verify_compressed_vector(original_vector, decimal_places, cv)

    assert type(cv.integer_part) == sdsl4py.int_vector_64, "Compressed vector should be of type int_vector_64"


def test_int_vector_32():
    original_vector, decimal_places = get_original_vector_and_decimal_places(32)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 32)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)
    verify_compressed_vector(original_vector, decimal_places, cv)

    assert type(cv.integer_part) == sdsl4py.int_vector_32, "Compressed vector should be of type int_vector_32"


def test_int_vector_16():
    original_vector, decimal_places = get_original_vector_and_decimal_places(16)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 16)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)
    verify_compressed_vector(original_vector, decimal_places, cv)

    assert type(cv.integer_part) == sdsl4py.int_vector_16, "Compressed vector should be of type int_vector_16"


def test_int_vector_8():
    original_vector, decimal_places = get_original_vector_and_decimal_places(8)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 8)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)
    verify_compressed_vector(original_vector, decimal_places, cv)

    assert type(cv.integer_part) == sdsl4py.int_vector_8, "Compressed vector should be of type int_vector_8"

def test_get_decompressed():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Set decompression configuration
    cv.set_decompressed_config(True)

    # Verify that the decompressed values match the original values
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Decompressed value {value} does not match original {original_vector[i]}"
        
    # Also verify slice, tuple, and list as get parameters
    # when accesing with index random
    import random
    random_index = random.randint(0, len(original_vector) - 1)
    assert round(cv[random_index], decimal_places) == round(original_vector[random_index], decimal_places), \
        f"Decompressed value {cv[random_index]} does not match original {original_vector[random_index]}"
    
    # when accessing with slice
    start_index = 0
    end_index = 3
    sliced_values = original_vector[start_index:end_index]
    cv_sliced_values = cv[start_index:end_index]
    for i in range(start_index, end_index):
        assert round(cv_sliced_values[i - start_index], decimal_places) == round(sliced_values[i], decimal_places), \
            f"Decompressed value {cv_sliced_values[i - start_index]} does not match original {sliced_values[i]}"
        
    # when accessing with tuple
    indices_tuple = (0, 1, 2)
    cv_tuple_values = cv[indices_tuple]
    # original_tuple_values = original_vector[indices_tuple]
    original_as_numpy = np.asarray(original_vector)
    original_tuple_values = original_as_numpy[list(indices_tuple)]  # Convert tuple to list for numpy indexing
    for i in range(len(indices_tuple)):
        assert round(cv_tuple_values[i], decimal_places) == round(original_tuple_values[i], decimal_places), \
            f"Decompressed value {cv_tuple_values[i]} does not match original {original_tuple_values[i]}"

    # when accessing with list
    indices_list = [0, 1, 2]
    cv_list_values = cv[indices_list]
    original_as_numpy = np.asarray(original_vector)
    original_list_values = original_as_numpy[list(indices_list)]  # Convert to list for numpy indexing
    for i, index in enumerate(indices_list):
        assert round(cv_list_values[i], decimal_places) == round(original_list_values[index], decimal_places), \
            f"Decompressed value {cv_list_values[i]} does not match original {original_list_values[index]}"
        

def test_get_compressed():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Set decompression configuration to False
    cv.set_decompressed_config(False)

    # Verify that the decompressed values match the original values
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Decompressed value {value} does not match original {original_vector[i]}"
        
    # Also verify slice, tuple, and list as get parameters
    # when accesing with index random
    import random
    random_index = random.randint(0, len(original_vector) - 1)
    assert round(cv[random_index], decimal_places) == round(original_vector[random_index], decimal_places), \
        f"Decompressed value {cv[random_index]} does not match original {original_vector[random_index]}"
    
    # when accessing with slice
    start_index = 0
    end_index = 3
    sliced_values = original_vector[start_index:end_index]
    cv_sliced_values = cv[start_index:end_index]
    for i in range(start_index, end_index):
        assert round(cv_sliced_values[i - start_index], decimal_places) == round(sliced_values[i], decimal_places), \
            f"Decompressed value {cv_sliced_values[i - start_index]} does not match original {sliced_values[i]}"
        
    # when accessing with tuple
    indices_tuple = (0, 1, 2)
    cv_tuple_values = cv[indices_tuple]
    # original_tuple_values = original_vector[indices_tuple]
    original_as_numpy = np.asarray(original_vector)
    original_tuple_values = original_as_numpy[list(indices_tuple)]  # Convert tuple to list for numpy indexing
    for i in range(len(indices_tuple)):
        assert round(cv_tuple_values[i], decimal_places) == round(original_tuple_values[i], decimal_places), \
            f"Decompressed value {cv_tuple_values[i]} does not match original {original_tuple_values[i]}"

    # when accessing with list
    indices_list = [0, 1, 2]
    cv_list_values = cv[indices_list]
    original_as_numpy = np.asarray(original_vector)
    original_list_values = original_as_numpy[list(indices_list)]  # Convert to list for numpy indexing
    for i, index in enumerate(indices_list):
        assert round(cv_list_values[i], decimal_places) == round(original_list_values[index], decimal_places), \
            f"Decompressed value {cv_list_values[i]} does not match original {original_list_values[index]}"

def test_compress_enc_vector_elias_delta():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using Elias delta encoding
    cv.compress(sdsl4py.enc_vector_elias_delta)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"
        
def test_compress_vlc_vector_elias_delta():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using VLC Elias delta encoding
    cv.compress(sdsl4py.vlc_vector_elias_delta)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"
        
def test_compress_dac_vector():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using DAC encoding
    cv.compress(sdsl4py.dac_vector)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"
        

def test_compress_enc_vector_elias_gamma():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using Elias gamma encoding
    cv.compress(sdsl4py.enc_vector_elias_gamma)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"

def test_compress_enc_vector_fibonacci():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using Fibonacci encoding
    cv.compress(sdsl4py.enc_vector_fibonacci)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"

def test_compress_enc_vector_comma_2():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using Comma-2 encoding
    cv.compress(sdsl4py.enc_vector_comma_2)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"

def test_compress_vlc_vector_elias_gamma():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using VLC Elias gamma encoding
    cv.compress(sdsl4py.vlc_vector_elias_gamma)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"

def test_compress_vlc_vector_fibonacci():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using VLC Fibonacci encoding
    cv.compress(sdsl4py.vlc_vector_fibonacci)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"

def test_compress_vlc_vector_comma_2():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    # Compress the vector using VLC Comma-2 encoding
    cv.compress(sdsl4py.vlc_vector_comma_2)

    # Verify that the compressed vector can be iterated over
    for value in cv:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")
    
    # verify all values are still correct
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Compressed value {value} does not match original {original_vector[i]}"
        

def test_build_from_file():
    original_vector, decimal_places = get_original_vector_and_decimal_places(64)
    # Create the compressed vector
    cv = CompressedVector(decimal_places, 64)
    cv.create_vector(len(original_vector))
    
    # Save the original vector to a file
    np.savetxt('original_vector.csv', original_vector, delimiter=',')
    
    # Fill the compressed vector from the file
    cv.build_from_file('original_vector.csv', column=0, delimiter=',')
    
    # assert size is correct
    assert len(cv) == len(original_vector), "Compressed vector size does not match original vector size"
    # Verify that the decompressed values match the original values
    for i, value in enumerate(cv):
        assert round(value, decimal_places) == round(original_vector[i], decimal_places), \
            f"Decompressed value {value} does not match original {original_vector[i]}"
        
if __name__ == "__main__":
    test_fill_from_file()