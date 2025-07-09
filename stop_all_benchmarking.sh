#!/bin/bash

# List of experiment module names
exp_list=(
    "all_libraries"
    "all_libraries_memory_allocation"
    "build_compressed_vector"
    "compress"
    "plot_altair"
    "plot_altair_memory_allocation"
    "plot_altair_plus_building"
    "plot_pygal"
    "plot_pygal_memory_allocation"
    "sizes_comparison"
)

for exp in "${exp_list[@]}"; do
    echo "Killing process for $exp"
    pkill -f "python -m benchmarking.$exp"
done
