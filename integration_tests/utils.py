import sys
import json
import os
from datetime import datetime
import numpy as np
from compressed_vector import CompressedVector

import sdsl4py  # only if needed here

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "output", "compression_results.json")
INT_WIDTH = 8
DECIMAL_PLACES = 2
VECTOR_SIZE = 10000

import random

def get_original_vector_and_decimal_places(width, vector_size=VECTOR_SIZE):
    if width <= 16:
        # Low-precision: use small numbers and round to 2 decimal places
        decimal_places = 2
        base_values = [-12.56, 0.01, 98.43, -42.0, 0.99]
        vector = base_values + [round(random.uniform(-100, 100), decimal_places) for _ in range(vector_size - len(base_values))]
    else:
        # High-precision: use larger and more precise numbers, rounded to 8 decimal places
        decimal_places = 8
        base_values = [1234.5678, 0.00012345, 98765.4321, 42.0, 0.99999999]
        vector = base_values + [round(random.uniform(-1e5, 1e5), decimal_places) for _ in range(vector_size - len(base_values))]

    return vector, decimal_places

def get_original_vector_and_decimal_places_with_file(file_path, width):
    """
    Reads a vector from a file and returns it along with the decimal places.
    The file should contain data with columns separated by semicolons (;).
    This function extracts the values from column 1 (0-indexed).
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    vector = []
    for line in lines:
        columns = line.strip().split(';')
        if len(columns) > 1:  # Ensure there's at least 2 columns
            vector.append(float(columns[1]))  # Column 1 (0-indexed)
    
    if width <= 16:
        decimal_places = 2
    else:
        decimal_places = 8

    return vector, decimal_places

def verify_compressed_vector(original_vector, decimal_places, compressed_vector):
    # Verify that the reconstructed values match the original values
    reconstructed_values = list(compressed_vector)
    for original, reconstructed in zip(original_vector, reconstructed_values):
        assert round(original, decimal_places) == round(reconstructed, decimal_places), \
            f"Original: {original}, Reconstructed: {reconstructed}"

    # Verify the size in bytes is greater than zero
    size_in_bytes = compressed_vector.size_in_bytes()
    assert size_in_bytes > 0, "Size in bytes should be greater than zero"
    print(f"Size in bytes: {size_in_bytes}")

    # Verify that the compressed vector can be iterated over
    for value in compressed_vector:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")

def verify_not_compressed_vector(original_vector, decimal_places, compressed_vector):
    # Verify that the reconstructed values match the original values
    reconstructed_values = list(compressed_vector)
    for original, reconstructed in zip(original_vector, reconstructed_values):
        assert round(original, decimal_places) == round(reconstructed, decimal_places), \
            f"Original: {original}, Reconstructed: {reconstructed}"

    # Verify the size in bytes is greater than zero
    size_in_bytes = sys.getsizeof(compressed_vector)
    assert size_in_bytes > 0, "Size in bytes should be greater than zero"
    print(f"Size in bytes: {size_in_bytes}")

    # Verify that the compressed vector can be iterated over
    for value in compressed_vector:
        assert isinstance(value, float), "Value should be a float"
        print(f"Value: {value}")

def get_test_vector(size=VECTOR_SIZE, decimal_places=DECIMAL_PLACES, int_width=INT_WIDTH):
    # Scale factor based on decimal precision
    scale = 10 ** decimal_places

    # Max value for decimal part that fits in given bit width
    max_decimal = min(scale - 1, 2 ** int_width - 1)

    # Generate random decimal values and integer parts
    decimal_parts = np.random.randint(0, max_decimal + 1, size)
    integer_parts = np.random.uniform(-1, 1, size).astype(int)

    # Combine and round
    vector = (integer_parts + decimal_parts / scale).round(decimal_places)
    return vector.tolist()


def run_compression_method(name, method=None, vector_size=VECTOR_SIZE, decimal_places=DECIMAL_PLACES, width=INT_WIDTH):
    original_vector = get_test_vector(vector_size, decimal_places, width)
    original_size = sys.getsizeof(original_vector)

    cv = CompressedVector(int_width=width, decimal_places=decimal_places)
    cv.create_vector(len(original_vector))
    cv.fill_from_vector(original_vector)

    if method is not None:
        try:
            cv.compress(method)
        except Exception as e:
            print(f"Error compressing with {name}: {e}")
            cv.destroy()
            return {
                "name": name,
                "success": False,
                "error": str(e),
                "size_bytes": 0,
                "percentage": 0
            }

    # Decompression accuracy check
    EPSILON = 10 ** -decimal_places
    for i in range(len(original_vector)):
        if abs(cv[i] - original_vector[i]) > EPSILON:
            index = i
            expected = original_vector[i]
            got = cv[i]
            size = cv.size_in_bytes()
            print(f"Error: Value mismatch at index {index}. Expected {expected}, got {got}")
            cv.destroy()
            return {
                "name": name,
                "success": False,
                "error": f"Value mismatch at index {index}. Expected {expected}, got {got}",
                "size_bytes": size,
                "percentage": (size / original_size) * 100
            }

    compressed_size = cv.size_in_bytes()
    percentage = (compressed_size / original_size) * 100
    cv.destroy()
    return {
        "name": name,
        "success": True,
        "size_bytes": compressed_size,
        "original_size": original_size,
        "percentage": percentage,
        "timestamp": datetime.now().isoformat(),
        "vector_size": vector_size,
        "decimal_places": decimal_places,
        "width": width
    }


def save_result(result):
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
        except json.JSONDecodeError:
            results = []
    else:
        results = []

    result_name = result["name"]
    for i, existing_result in enumerate(results):
        if existing_result.get("name") == result_name:
            results[i] = result
            break
    else:
        results.append(result)

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {RESULTS_FILE}")

if  __name__ == "__main__":
    # Example usage
    result = run_compression_method("Example Method", method=sdsl4py.dac_vector)
    save_result(result)
    print(f"Test vector: {get_test_vector()}")
    print(f"Compression result: {result}")