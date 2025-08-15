import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import pandas as pd

folder_sensores     = "./benchmarking/input/dataset_bridge"
delimiter           = ";"
output_folder       = "./benchmarking/output/justificacion"

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

x_column = 0
y_column = 1
range_points = [6000, 12000, 20000, 70000, 100000, 300000]

# Dictionary to store statistics for all files
all_stats = {}

for file in os.listdir(folder_sensores):
    if file.endswith(".txt"):
        file_path = os.path.join(folder_sensores, file)
        output_file = os.path.join(output_folder, f"{file[:-4]}_plot.png")
        output_range_file = os.path.join(output_folder, f"{file[:-4]}_range.png")
        
        # Read the data
        try:
            data = np.genfromtxt(file_path, delimiter=delimiter, skip_header=1, filling_values=np.nan)
        except ValueError as e:
            print(f"Error reading {file}: {e}")
            print(f"Trying alternative reading method...")
            try:
                # Try reading with pandas for better error handling
                df = pd.read_csv(file_path, delimiter=delimiter, header=0, on_bad_lines='skip')
                data = df.values
                print(f"Successfully read {file} with pandas (shape: {data.shape})")
            except Exception as e2:
                print(f"Failed to read {file} with both methods: {e2}")
                continue
        
        # Check if data has the required columns
        if data.shape[1] <= max(x_column, y_column):
            print(f"Skipping {file}: insufficient columns (has {data.shape[1]}, needs {max(x_column, y_column)+1})")
            continue
        
        # Create the original plot
        plt.figure()
        plt.plot(data[:, x_column], data[:, y_column])
        plt.title(f"Plot of {file}")
        plt.xlabel(f"Column {x_column}")
        plt.ylabel(f"Column {y_column}")
        
        # Save the original plot
        plt.savefig(output_file)
        plt.close()
        
        print(f"Plot saved to {output_file}")
        
        # Create the range plot
        plt.figure()
        valid_points = [n for n in range_points if n < len(data)]
        if valid_points:
            x_range = []
            y_range = []
            
            # Store statistics for this file
            file_stats = {
                'filename': file[:-4],
                'total_points': len(data),
                'ranges': {},
                'range_values': []
            }
            
            for n in valid_points:
                # Calculate the range (max - min) from 0 to n
                y_subset = data[:n, y_column]
                range_value = np.max(y_subset) - np.min(y_subset)
                x_range.append(n)
                y_range.append(range_value)
                
                # Store range for each point
                file_stats['ranges'][n] = range_value
                file_stats['range_values'].append(range_value)
            
            # Calculate statistics for range variability
            if len(file_stats['range_values']) > 1:
                file_stats['range_mean'] = np.mean(file_stats['range_values'])
                file_stats['range_std'] = np.std(file_stats['range_values'])
                file_stats['range_cv'] = file_stats['range_std'] / file_stats['range_mean']  # Coefficient of variation
                file_stats['range_min'] = np.min(file_stats['range_values'])
                file_stats['range_max'] = np.max(file_stats['range_values'])
                file_stats['range_growth_rate'] = (file_stats['range_max'] - file_stats['range_min']) / file_stats['range_min']
            
            all_stats[file[:-4]] = file_stats
            
            plt.plot(x_range, y_range, 'o-')
            plt.title(f"Range Plot of {file}")
            plt.xlabel("Data Points (0 to N)")
            plt.ylabel("Range (Max - Min)")
            plt.grid(True)
            
            # Save the range plot
            plt.savefig(output_range_file)
            plt.close()
            
            print(f"Range plot saved to {output_range_file}")
        else:
            print(f"No valid range points for {file} (data length: {len(data)})")

# Create summary table
if all_stats:
    # Prepare data for the table
    table_data = []
    for filename, stats in all_stats.items():
        row = {
            'File': filename,
            'Total Points': stats['total_points'],
            'Range Mean': f"{stats.get('range_mean', 0):.2f}",
            'Range Std': f"{stats.get('range_std', 0):.2f}",
            'Coeff. of Variation': f"{stats.get('range_cv', 0):.4f}",
            'Range Growth Rate': f"{stats.get('range_growth_rate', 0):.4f}",
        }
        
        # Add individual range values
        for point in range_points:
            if point in stats['ranges']:
                row[f'Range@{point}'] = f"{stats['ranges'][point]:.2f}"
            else:
                row[f'Range@{point}'] = "N/A"
        
        table_data.append(row)
    
    # Create DataFrame and save as CSV
    df = pd.DataFrame(table_data)
    csv_output = os.path.join(output_folder, "range_variability_analysis.csv")
    df.to_csv(csv_output, index=False)
    
    print(f"\nStatistics table saved to {csv_output}")
    
    # Print formatted table
    print("\n=== RANGE VALUES TABLE ===")
    
    # Create header
    header = ["File"] + [f"Range@{point}" for point in range_points]
    
    # Calculate column widths
    col_widths = []
    for i, col in enumerate(header):
        if i == 0:  # File column
            max_width = max(len(col), max(len(stats['filename']) for stats in all_stats.values()))
        else:  # Range columns
            point = range_points[i-1]
            max_width = max(len(col), max(len(f"{stats['ranges'].get(point, 0):.2f}") 
                                         for stats in all_stats.values() if point in stats['ranges']))
        col_widths.append(max_width + 2)
    
    # Print header
    header_row = "|".join(f" {header[i]:<{col_widths[i]-1}}" for i in range(len(header)))
    print(header_row)
    print("-" * len(header_row))
    
    # Print data rows
    for filename, stats in all_stats.items():
        row_data = [filename]
        for point in range_points:
            if point in stats['ranges']:
                row_data.append(f"{stats['ranges'][point]:.2f}")
            else:
                row_data.append("N/A")
        
        data_row = "|".join(f" {row_data[i]:<{col_widths[i]-1}}" for i in range(len(row_data)))
        print(data_row)
    
    # Print summary statistics
    print("\n=== RANGE VARIABILITY ANALYSIS ===")
    print(f"Number of files analyzed: {len(all_stats)}")
    
    # Calculate overall statistics
    all_cvs = [stats.get('range_cv', 0) for stats in all_stats.values() if 'range_cv' in stats]
    all_growth_rates = [stats.get('range_growth_rate', 0) for stats in all_stats.values() if 'range_growth_rate' in stats]
    
    if all_cvs:
        print(f"Average Coefficient of Variation: {np.mean(all_cvs):.4f} (±{np.std(all_cvs):.4f})")
        print(f"Average Growth Rate: {np.mean(all_growth_rates):.4f} (±{np.std(all_growth_rates):.4f})")
        print(f"CV Range: {np.min(all_cvs):.4f} to {np.max(all_cvs):.4f}")
        print(f"Growth Rate Range: {np.min(all_growth_rates):.4f} to {np.max(all_growth_rates):.4f}")
        
        # Conclusion
        cv_similarity = np.std(all_cvs) / np.mean(all_cvs) if np.mean(all_cvs) > 0 else 0
        print(f"\nSimilarity Index (lower = more similar): {cv_similarity:.4f}")
        if cv_similarity < 0.2:
            print("CONCLUSION: Files show VERY SIMILAR range variability patterns")
        elif cv_similarity < 0.5:
            print("CONCLUSION: Files show SIMILAR range variability patterns")
        else:
            print("CONCLUSION: Files show DIFFERENT range variability patterns")
