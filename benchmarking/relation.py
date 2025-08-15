import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Define las rutas de las carpetas
access_path = "./OUTPUT/SDSL4Py Access Time Comparison/tables/"
build_path = "./OUTPUT/SDSL4Py Compression Time Comparison/tables/"
space_path = "./OUTPUT/SDSL4Py Compression Space Comparison/tables/"

# Función para leer y concatenar todos los CSV de una carpeta
def read_all_csvs(folder):
    all_files = glob.glob(os.path.join(folder, "*.csv"))
    df_list = [pd.read_csv(f) for f in all_files]
    return pd.concat(df_list, ignore_index=True)

# Lee y concatena todos los archivos CSV de cada carpeta
access_df = read_all_csvs(access_path)
build_df = read_all_csvs(build_path)
space_df = read_all_csvs(space_path)

# Renombramos la columna 'mean' para diferenciar las métricas
access_df = access_df.rename(columns={"mean": "access_time"})
build_df = build_df.rename(columns={"mean": "build_time"})
space_df = space_df.rename(columns={"mean": "space_used"})

# Hacemos merge usando 'n_size' y 'option'
merged_df = access_df.merge(build_df, on=["n_size", "option"]).merge(space_df, on=["n_size", "option"])

# Excluimos "Original Data" de los datos
merged_df = merged_df[merged_df['option'] != 'Original Data']

# Agregamos los datos por 'option' (estructura) para tener un punto por estructura
aggregated_df = merged_df.groupby('option').agg({
    'access_time': 'mean',
    'build_time': 'mean', 
    'space_used': 'mean'
}).reset_index()

# Calculamos la distancia euclidiana desde el origen (0,0,0)
aggregated_df['euclidean_distance_from_origin'] = np.sqrt(
    aggregated_df['access_time']**2 + 
    aggregated_df['build_time']**2 + 
    aggregated_df['space_used']**2
).round(8)

# Encontramos el punto ideal (mínimos valores en cada métrica)
ideal_point = {
    'access_time': aggregated_df['access_time'].min(),
    'build_time': aggregated_df['build_time'].min(),
    'space_used': aggregated_df['space_used'].min()
}

# Calculamos la distancia euclidiana desde el punto ideal
aggregated_df['euclidean_distance_from_ideal'] = np.sqrt(
    (aggregated_df['access_time'] - ideal_point['access_time'])**2 + 
    (aggregated_df['build_time'] - ideal_point['build_time'])**2 + 
    (aggregated_df['space_used'] - ideal_point['space_used'])**2
).round(8)

# Ordenamos por distancia desde el origen (0,0,0) (menor es mejor)
aggregated_df_sorted = aggregated_df.sort_values('euclidean_distance_from_origin')

# Creamos el directorio scatter_plot si no existe
os.makedirs('./OUTPUT/scatter_plot', exist_ok=True)

# Plot 1: 3D scatter plot SIN punto ideal
fig1 = plt.figure(figsize=(12, 9))
ax1 = fig1.add_subplot(111, projection='3d')

# Obtenemos las opciones únicas para asignar colores diferentes
options = aggregated_df['option'].unique()
colors = plt.cm.tab10(np.linspace(0, 1, len(options)))

# Creamos el scatter plot con un punto por opción
for i, option in enumerate(options):
    option_data = aggregated_df[aggregated_df['option'] == option]
    ax1.scatter(option_data['access_time'], 
               option_data['build_time'], 
               option_data['space_used'],
               c=[colors[i]], 
               label=option, 
               alpha=0.8,
               s=100)

ax1.set_xlabel('Access Time (mean)', fontsize=12, labelpad=10)
ax1.set_ylabel('Build Time (mean)', fontsize=12, labelpad=10)
ax1.set_zlabel('Space Used (mean)', fontsize=12, labelpad=10)
ax1.set_title('3D Scatter Plot: Average Metrics by Structure Type', fontsize=14)
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig('./OUTPUT/scatter_plot/3d_scatter_plot_structures.png', dpi=300, bbox_inches='tight')
plt.show()
plt.close()

# Plot 2: Gráfico de barras de distancias desde el origen (0,0,0)
fig2, ax2 = plt.subplots(figsize=(12, 8))
bars = ax2.barh(aggregated_df_sorted['option'], aggregated_df_sorted['euclidean_distance_from_origin'])
ax2.set_xlabel('Euclidean Distance from Origin (0,0,0)', fontsize=12)
ax2.set_title('Distance from Origin (Lower is Better)', fontsize=14)
ax2.grid(True, alpha=0.3)

# Colorear las barras según la distancia
for i, bar in enumerate(bars):
    if i < len(bars) // 3:  # Best third
        bar.set_color('green')
        bar.set_alpha(0.7)
    elif i < 2 * len(bars) // 3:  # Middle third
        bar.set_color('orange')
        bar.set_alpha(0.7)
    else:  # Worst third
        bar.set_color('red')
        bar.set_alpha(0.7)

plt.tight_layout()
plt.savefig('./OUTPUT/scatter_plot/euclidean_distance_from_ideal.png', dpi=300, bbox_inches='tight')
plt.show()
plt.close()

# Generamos archivo LaTeX con la tabla de puntuaciones
latex_table = """\\begin{table}[h!]
\\centering
\\caption{Ranking of Data Structures by Euclidean Distance from Origin (0,0,0)}
\\label{tab:structure_ranking}
\\begin{tabular}{|c|l|c|c|c|c|}
\\hline
\\textbf{Rank} & \\textbf{Structure} & \\textbf{Access Time} & \\textbf{Build Time} & \\textbf{Space Used} & \\textbf{Euclidean Distance} \\\\
\\hline
"""

# Añadimos las filas de la tabla
for idx, (_, row) in enumerate(aggregated_df_sorted.iterrows(), 1):
    structure_name = row['option'].replace('_', '\\_')  # Escape underscores for LaTeX
    latex_table += f"{idx} & {structure_name} & {row['access_time']:.8f} & {row['build_time']:.8f} & {row['space_used']:.8f} & {row['euclidean_distance_from_origin']:.8f} \\\\\n"
    latex_table += "\\hline\n"

latex_table += """\\end{tabular}
\\end{table}

% Additional statistics
\\begin{table}[h!]
\\centering
\\caption{Origin Point Coordinates}
\\label{tab:origin_point}
\\begin{tabular}{|l|c|}
\\hline
\\textbf{Metric} & \\textbf{Value} \\\\
\\hline
Access Time & 0.00000000 \\\\
\\hline
Build Time & 0.00000000 \\\\
\\hline
Space Used & 0.00000000 \\\\
\\hline
\\end{tabular}
\\end{table}
"""

# Guardamos la tabla LaTeX en un archivo .txt
with open('./OUTPUT/scatter_plot/latex_ranking_table.txt', 'w', encoding='utf-8') as f:
    f.write(latex_table)

print("Archivo LaTeX generado: ./OUTPUT/scatter_plot/latex_ranking_table.txt")

# Eliminamos los otros plots que no se requieren
# Plot 3 y Plot 4 removidos

# Mostramos los datos agregados con distancias euclidianas
print("Métricas promedio por estructura (un punto por estructura):")
print(aggregated_df.round(8).to_string(index=False))

print(f"\nPunto de referencia (origen):")
print(f"Access Time: 0.00000000")
print(f"Build Time: 0.00000000")
print(f"Space Used: 0.00000000")

print("\nRanking por distancia euclidiana desde el origen (0,0,0) (mejor a peor):")
ranking_df = aggregated_df_sorted[['option', 'euclidean_distance_from_origin']].reset_index(drop=True)
ranking_df.index += 1  # Start ranking from 1
print(ranking_df.to_string())

print("\nRanking por distancia euclidiana desde el punto ideal:")
ranking_ideal_df = aggregated_df.sort_values('euclidean_distance_from_ideal')[['option', 'euclidean_distance_from_ideal']].reset_index(drop=True)
ranking_ideal_df.index += 1
print(ranking_ideal_df.to_string())

# También creamos un resumen estadístico por opción (del dataset original)
summary_stats = merged_df.groupby('option').agg({
    'access_time': ['mean', 'std', 'count'],
    'build_time': ['mean', 'std', 'count'], 
    'space_used': ['mean', 'std', 'count']
}).round(8)

print("\nEstadísticas detalladas por estructura (incluyendo variabilidad):")
print(summary_stats)
