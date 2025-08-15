from benchmarking.exp_runner import setup_experiment
from cv_visualization import COMPRESSION_METHODS
import sdsl4py as sdsl
import time
import numpy as np
import random

exp_name = "SDSL4Py Compression Time Comparison"
exp = setup_experiment(exp_name)


def generate_test_vectors(vector_type, size=10000):
    """Generate 4 different types of test vectors"""
    if vector_type == "incremental_small":
        # Valores crecientes con poca diferencia entre ellos
        x = list(range(1, size + 1))
        y = [i + random.uniform(0, 2) for i in range(1, size + 1)]
    elif vector_type == "random":
        # Valores aleatorios
        x = [random.randint(1, size * 10) for _ in range(size)]
        y = [random.randint(1, size * 10) for _ in range(size)]
    elif vector_type == "oscillating":
        # Valores ascendentes y luego descendentes como oscilantes
        x = []
        y = []
        for i in range(size):
            # Create wave pattern
            wave_val = int(size/2 * (1 + np.sin(i * 4 * np.pi / size)))
            x.append(i + 1)
            y.append(wave_val)
    elif vector_type == "incremental_large":
        # Valores ascendentes pero con mucha diferencia entre si
        x = list(range(1, size + 1))
        y = [i * random.randint(50, 200) for i in range(1, size + 1)]
    else:
        raise ValueError(f"Unknown vector type: {vector_type}")
    
    return x, y


@exp.config
def default_config():
    int_widths = [8]
    vector_types = ["incremental_small", "random", "oscillating", "incremental_large"]
    cases = []
    
    # Add original data cases for each vector type
    for vector_type in vector_types:
        cases.append({
            "option": f"Original Data - {vector_type}",
            "vector_type": vector_type
        })
    
    # Add compressed cases for each vector type and compression method
    for vector_type in vector_types:
        for method in COMPRESSION_METHODS:
            if method.startswith("enc_vector"):
                # Only use 64-bit width for enc_vector
                cases.append({
                    "option": f"{method} - 64 - {vector_type}",
                    "vector_type": vector_type,
                    "compress_option": method,
                    "int_width": 64
                })
            else:
                # Use all widths for other compression methods
                for int_width in int_widths:
                    cases.append({
                        "option": f"{method} - {int_width} - {vector_type}",
                        "vector_type": vector_type,
                        "compress_option": method,
                        "int_width": int_width
                    })

@exp.automain
def run(cases, iterations, vector_size=10000):
    def experiment_fn(x, y, option):
        start = time.perf_counter()
        if option.startswith("Original Data"):
            # No compression, just return the time for data preparation
            # but make sure is abs(int())
            cx, cy = x, y
            end = time.perf_counter()
            return end - start
        else:
            # Extract parameters from option string
            parts = option.split(" - ")
            int_width = int(parts[1])
            compress_method = parts[0]

            # Create vectors for x and y
            x_vector = None
            y_vector = None
            
            # Initialize appropriate sized vectors based on int_width
            if int_width == 8:
                x_vector = sdsl.int_vector_8(size=len(x), default_value=0)
                y_vector = sdsl.int_vector_8(size=len(y), default_value=0)
            elif int_width == 16:
                x_vector = sdsl.int_vector_16(size=len(x), default_value=0)
                y_vector = sdsl.int_vector_16(size=len(y), default_value=0)
            elif int_width == 32:
                x_vector = sdsl.int_vector_32(size=len(x), default_value=0)
                y_vector = sdsl.int_vector_32(size=len(y), default_value=0)
            elif int_width == 64:
                x_vector = sdsl.int_vector_64(size=len(x), default_value=0)
                y_vector = sdsl.int_vector_64(size=len(y), default_value=0)
            
            # Fill the vectors with values from x and y (convert to int)
            for i in range(len(x)):
                x_vector[i] = abs(int(x[i]))
            
            for i in range(len(y)):
                y_vector[i] = abs(int(y[i]))
            
            compress_method_fn = COMPRESSION_METHODS.get(compress_method, None)
            if compress_method_fn is None:
                end = time.perf_counter()
                return end - start
            else:
                compressed_x = compress_method_fn(x_vector)
                compressed_y = compress_method_fn(y_vector)

        end = time.perf_counter()
        return end - start

    results = {}
    
    for case in cases:
        option = case["option"]
        vector_type = case["vector_type"]
        
        # Generate test vectors for this case
        x, y = generate_test_vectors(vector_type, vector_size)
        
        print(f"⏱️ Testing compression time for {option} with {len(x)} elements...")
        
        # Run multiple iterations for this case
        differences = []
        for iteration in range(iterations):
            time_result = experiment_fn(x, y, option)
            differences.append(time_result)
        
        # Calculate statistics
        import statistics
        results[option] = {
            "option": option,
            "vector_type": vector_type,
            "vector_size": len(x),
            "mean": statistics.mean(differences),
            "stdev": statistics.stdev(differences) if len(differences) > 1 else 0,
            "min": min(differences),
            "max": max(differences),
            "all_differences": differences,
            "iterations": iterations,
            "measurement_unit": "seconds"
        }
        
        print(f"✅ {option}: {statistics.mean(differences):.6f}s avg")
    
    exp.log_scalar("num_cases", len(results))
    return results
