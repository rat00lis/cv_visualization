# run all experiments in benchmarking/ with nohup python -m benchmarking.exp_name > benchmarking/output/logs/exp_name.log &

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
    echo "Running $exp"
    nohup python -m benchmarking.$exp > benchmarking/output/logs/$exp.log 2>&1 &
done