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

def get_test_vector(size=VECTOR_SIZE, decimal_places=DECIMAL_PLACES):
    return np.round(np.random.uniform(-1, 1, size), decimal_places).tolist()

def run_compression_method(name, method=None, vector_size=VECTOR_SIZE, decimal_places=DECIMAL_PLACES, width=INT_WIDTH):
    original_vector = get_test_vector(vector_size, decimal_places)
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
    
    for i in range(len(original_vector)):
        print(cv[i], end=' ')
    print(original_vector)
    compressed_size = cv.size_in_bytes()
    percentage = (compressed_size / original_size) * 100
    print(f"{name}: {compressed_size:,} bytes ({percentage:.2f}% of original)")
    # verify the compressed vector
    for i in range(len(original_vector)):
        if cv[i] != original_vector[i]:
            index = i
            expected = original_vector[i]
            got = cv[i]
            print(f"Error: Value mismatch at index {index}. Expected {expected}, got {got}")
            cv.destroy()
            return {
                "name": name,
                "success": False,
                "error": f"Value mismatch at index {index}. Expected {expected}, got {got}",
                "size_bytes": compressed_size,
                "percentage": percentage
            }
    
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

    # Check if result with same name exists and replace it
    result_name = result["name"]
    for i, existing_result in enumerate(results):
        if existing_result.get("name") == result_name:
            results[i] = result
            break
    else:
        # If no match was found, append the new result
        results.append(result)

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {RESULTS_FILE}")

