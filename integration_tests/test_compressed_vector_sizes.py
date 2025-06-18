import pytest
import numpy as np
from compressed_vector import CompressedVector
import sdsl4py
import pandas as pd
import os
import matplotlib.pyplot as plt
import sys

def test_compression_sizes():
    """Test to measure and compare sizes of different compression methods."""
    # Create a vector with random numbers between -1 and 1, limited to 4 decimal places
    original_vector = np.round(np.random.uniform(-1, 1, 100000), 2).tolist()
    decimal_places = 2  # Update to match our actual precision
    width = 8
    
    # Calculate the size of the original Python list in memory
    original_size = sys.getsizeof(original_vector)
    
    # Define compression methods to test, including the CompressedVector without additional compression
    compression_methods = [
        ("CompressedVector (No Compression)", None),
        ("Elias Delta", sdsl4py.enc_vector_elias_delta),
        ("VLC Elias Delta", sdsl4py.vlc_vector_elias_delta),
        ("DAC Vector", sdsl4py.dac_vector),
        ("Elias Gamma", sdsl4py.enc_vector_elias_gamma),
        ("Fibonacci", sdsl4py.enc_vector_fibonacci),
        ("Comma-2", sdsl4py.enc_vector_comma_2),
        ("VLC Elias Gamma", sdsl4py.vlc_vector_elias_gamma),
        ("VLC Fibonacci", sdsl4py.vlc_vector_fibonacci),
        ("VLC Comma-2", sdsl4py.vlc_vector_comma_2)
    ]
    
    # Prepare results storage
    results = {
        "Compression Method": [],
        "Size (bytes)": [],
        "Percentage of Original": []
    }
    
    # Add original size to results
    results["Compression Method"].append("Original Python List")
    results["Size (bytes)"].append(original_size)
    results["Percentage of Original"].append(100.0)
    
    # Test each compression method
    for name, method in compression_methods:
        # Create a new vector with the same data
        cv = CompressedVector(
            int_width=width,
            decimal_places=decimal_places
        )
        cv.create_vector(len(original_vector))
        cv.fill_from_vector(original_vector)
        
        # Apply compression if a method is specified
        if method is not None:
            cv.compress(method)
        
        # Measure size
        compressed_size = cv.size_in_bytes()
        percentage = (compressed_size / original_size) * 100
        
        # Store results
        results["Compression Method"].append(name)
        results["Size (bytes)"].append(compressed_size)
        results["Percentage of Original"].append(percentage)
        
        # Print results for immediate feedback
        print(f"{name}: {compressed_size:,} bytes ({percentage:.2f}% of original)")
        cv.destroy()  # Clean up the CompressedVector instance
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    csv_path = os.path.join(os.path.dirname(__file__), "compression_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"Results saved to {csv_path}")
    
    # Create a bar chart
    plt.figure(figsize=(12, 8))
    plt.bar(df["Compression Method"], df["Percentage of Original"])
    plt.title("Compression Methods Comparison")
    plt.xlabel("Method")
    plt.ylabel("Size (% of original Python list)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    # Save the plot
    plot_path = os.path.join(os.path.dirname(__file__), "compression_results.png")
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
    # Don't return the DataFrame in pytest mode
    if __name__ == "__main__":
        return df
    # Add at least one assertion for pytest
    assert len(results["Compression Method"]) > 1, "Failed to generate compression results"

if __name__ == "__main__":
    # This allows running the test directly (not through pytest)
    df = test_compression_sizes()
    # You could add additional analysis of the DataFrame here
    print(df)