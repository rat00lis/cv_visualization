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
VECTOR_SIZE = 10


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
