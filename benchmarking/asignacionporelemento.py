#!/usr/bin/env python3
import argparse
import sys
import pandas as pd
import numpy as np
import os

def latex_escape(text: str) -> str:
    return str(text).replace("_", "\\_")

def nice_variant(name: str) -> str:
    return str(name).replace("Compressed Vector Downsample - ", "CVD - ")

def main():
    p = argparse.ArgumentParser(
        description="Memoria por elemento (resultado/puntos) en tabla ANCHA: una fila por n_size y una columna por variante (excluye 'Original Data')."
    )
    p.add_argument("csv", nargs="?", default="-", help="Ruta al CSV (o - para stdin).")
    p.add_argument("--out", choices=["latex", "markdown", "csv"], default="latex",
                   help="Formato de salida (por defecto: latex).")
    p.add_argument("--round", type=int, default=2, help="Decimales (por defecto: 2).")
    p.add_argument("--caption", "-c", default=None, help="Caption LaTeX.")
    p.add_argument("--label", "-l", default=None, help="Label LaTeX.")
    p.add_argument("--table-size", default="", help="Comando antes del tabular, p.ej. \\small")
    p.add_argument("--orig-name", dest="orig_name", default="Original Data",
                   help="Nombre exacto de la opción Original (por defecto: 'Original Data').")
    p.add_argument("--nout", type=int, default=1000,
                   help="n_out fijo para TODAS las opciones ≠ 'Original Data' (por defecto: 1000).")
    args = p.parse_args()

    # Caption/label por defecto
    if args.csv != "-" and args.caption is None:
        filename = os.path.splitext(os.path.basename(args.csv))[0]
        args.caption = f"\\textit{{{latex_escape(filename)}}} – Memoria por elemento"
    elif args.caption is None:
        args.caption = "Memoria por elemento (resultado/puntos, sin Original)"
    if args.csv != "-" and args.label is None:
        filename = os.path.splitext(os.path.basename(args.csv))[0]
        args.label = f"tab:{latex_escape(filename)}_mem_por_elemento_sin_original"
    elif args.label is None:
        args.label = "tab:mem_por_elemento_sin_original"

    # Leer CSV
    if args.csv == "-" and sys.stdin.isatty():
        print("Leyendo desde stdin, pega tu CSV y presiona Ctrl+D (Linux/Mac) o Ctrl+Z + Enter (Windows).", file=sys.stderr)
    df = pd.read_csv(sys.stdin if args.csv == "-" else args.csv)

    # Validaciones
    required = {"option", "n_size", "mean"}
    if not required.issubset(df.columns):
        faltan = ", ".join(sorted(required - set(df.columns)))
        raise SystemExit(f"Faltan columnas requeridas: {faltan}")
    df["option"] = df["option"].astype(str).str.strip()

    # --- REGLA DE PUNTOS ---
    # Cualquier opción ≠ 'Original Data' divide por 1000; 'Original Data' se excluye.
    # Primero calculamos puntos según esa regla (aunque luego filtremos Original).
    df["_points"] = np.where(df["option"] == args.orig_name, df["n_size"], args.nout)
    df["_points"] = pd.to_numeric(df["_points"], errors="coerce")
    df.loc[(df["_points"].isna()) | (df["_points"] <= 0), "_points"] = np.nan

    # Memoria por elemento (convierte KB -> bits; ajusta si tu unidad es otra)
    KB_to_bits =1
    df["mem_per_point"] = (df["mean"] * KB_to_bits) / df["_points"]

    # EXCLUIR 'Original Data'
    df = df[df["option"] != args.orig_name].copy()

    # Nombre bonito + pivot ancho
    df["variant_nice"] = df["option"].apply(nice_variant)
    wide = df.pivot_table(index="n_size", columns="variant_nice",
                          values="mem_per_point", aggfunc="mean")

    # Orden columnas: CVD-* (alfabético), TS Downsample, resto
    cols = list(wide.columns)
    cvd_cols = sorted([c for c in cols if c.startswith("CVD - ")])
    ts_nice = nice_variant("TS Downsample")
    ordered = cvd_cols + [c for c in [ts_nice] if c in cols] + [c for c in cols if c not in cvd_cols and c != ts_nice]
    wide = wide[ordered].sort_index()

    # Redondeo
    wide = wide.round(args.round)

    if args.out == "csv":
        print(wide.reset_index().to_csv(index=False))
        return

    if args.out == "markdown":
        out = wide.reset_index()
        headers = ["n_size"] + ordered
        print("| " + " | ".join(headers) + " |")
        print("|" + "|".join(["---:"] + [":---:"]*len(ordered)) + "|")
        for _, row in out.iterrows():
            vals = [str(int(row["n_size"]))] + [("" if pd.isna(row[c]) else str(row[c])) for c in ordered]
            print("| " + " | ".join(vals) + " |")
        return

    # LaTeX
    latex_df = wide.copy()
    latex_df.index.name = "n\\_size"
    latex_df.columns = [latex_escape(c) for c in ordered]
    body = latex_df.to_latex(
        index=True,
        escape=False,
        column_format="r" + "r"*len(ordered),
        float_format=lambda x: f"{x:.{args.round}f}"
    )

    print("\\begin{table}[H]")
    print("\\centering")
    if args.caption:
        print(f"\\caption{{{args.caption}}}")
    if args.label:
        print(f"\\label{{{args.label}}}")
    if args.table_size:
        print(args.table_size)
    print(body)
    print("\\end{table}")

if __name__ == "__main__":
    main()
