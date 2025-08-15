#!/usr/bin/env python3
import argparse
import sys
import pandas as pd
import numpy as np
import os

def latex_escape(text):
    """Escapa guiones bajos para LaTeX."""
    return str(text).replace("_", "\\_")

def main():
    p = argparse.ArgumentParser(description="Tabla de % de compactación de CVD vs TS y vs Original por n_size.")
    p.add_argument("csv", nargs="?", default="-", help="Ruta al CSV (o - para stdin).")
    p.add_argument("--out", choices=["markdown", "csv", "latex"], default="markdown",
                   help="Formato de salida (por defecto: markdown).")
    p.add_argument("--round", type=int, default=2, help="Decimales a redondear (por defecto: 2).")
    p.add_argument("--caption", "-c", default=None,
                   help="Caption para la tabla LaTeX (por defecto: generado desde el nombre del archivo).")
    p.add_argument("--label", "-l", default=None,
                   help="Label para la tabla LaTeX (por defecto: generado desde el nombre del archivo).")
    p.add_argument("--table-size", default="", help="Comando de tamaño LaTeX antes del tabular, por ej. \\small")
    args = p.parse_args()

    # Determinar caption y label si no se pasa explícitamente
    if args.csv != "-" and args.caption is None:
        filename = os.path.splitext(os.path.basename(args.csv))[0]
        args.caption = f"{latex_escape(filename)} – Tasa de compactación CVD vs TS vs Datos Originales"
    elif args.caption is None:
        args.caption = "Tasa de compactación CVD vs TS vs Datos Originales"

    if args.csv != "-" and args.label is None:
        filename = os.path.splitext(os.path.basename(args.csv))[0]
        args.label = f"tab:{latex_escape(filename)}_cvd_compactacion"
    elif args.label is None:
        args.label = "tab:cvd_compactacion"

    # Leer CSV
    if args.csv == "-" and sys.stdin.isatty():
        print("Leyendo desde stdin, pega tu CSV y presiona Ctrl+D (Linux/Mac) o Ctrl+Z + Enter (Windows).", file=sys.stderr)
    df = pd.read_csv(sys.stdin if args.csv == "-" else args.csv)

    # Normalizar nombres
    df["option"] = df["option"].str.strip()

    # Pivot: mean por n_size y option
    pivot = df.pivot_table(index="n_size", columns="option", values="mean", aggfunc="mean")

    # Identificar variantes CVD y baselines
    cvd_variants = [c for c in pivot.columns if c.lower().startswith("compressed vector downsample")]
    base_ts = "TS Downsample"
    base_orig = "Original Data"

    missing = [b for b in (base_ts, base_orig) if b not in pivot.columns]
    if missing:
        raise SystemExit(f"Faltan baselines en los datos: {', '.join(missing)}")

    # Calcular compactaciones por n_size y variante
    rows = []
    for n_size, row in pivot.iterrows():
        ts = row.get(base_ts, np.nan)
        od = row.get(base_orig, np.nan)
        for var in cvd_variants:
            val = row.get(var, np.nan)
            comp_vs_ts = np.nan if pd.isna(ts) or ts == 0 else 100.0 * (ts - val) / ts
            comp_vs_od  = np.nan if pd.isna(od) or od == 0 else 100.0 * (od - val) / od
            rows.append({
                "n_size": int(n_size),
                "variant": latex_escape(var.replace("Compressed Vector Downsample - ", "CVD - ")),
                "comp_vs_TS_%": comp_vs_ts,
                "comp_vs_Original_%": comp_vs_od
            })

    out = pd.DataFrame(rows).sort_values(["n_size", "variant"]).round(args.round)

    # Salidas
    if args.out == "markdown":
        print("| n_size | variant | comp_vs_TS_% | comp_vs_Original_% |")
        print("|-------:|:--------|------------:|-------------------:|")
        for _, r in out.iterrows():
            print(f"| {r['n_size']} | {r['variant']} | {r['comp_vs_TS_%']} | {r['comp_vs_Original_%']} |")

    elif args.out == "csv":
        print(out.to_csv(index=False))

    else:  # latex con \begin{table}[H]
        latex_df = out.rename(columns={
            "n_size": "n\\_size",
            "variant": "Variante",
            "comp_vs_TS_%": "Comp. vs TS (\\%)",
            "comp_vs_Original_%": "Comp. vs Original (\\%)"
        })
        body = latex_df.to_latex(index=False, escape=False, column_format="rlrr", float_format=lambda x: f"{x:.{args.round}f}")
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
