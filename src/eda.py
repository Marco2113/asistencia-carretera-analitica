#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDA reproducible (CLI) para el proyecto Asistencia Carretera.

Genera figuras PNG en reports/figs/ y (opcionalmente) un mapa HTML en reports/mapas/.

Incluye:
- Histograma de Tiempo_Respuesta_min (recorte p95)
- Boxplot de Costo_EUR por Tipo_Incidencia (recorte p98)
- Barras: incidencias por Ciudad (Top N)
- Serie mensual: incidencias por Mes y Año
- Heatmap de correlación numérica
- Barras: % SLA incumplido por Ciudad
- (Opcional) Mapa Folium (puntos y HeatMap)

Uso:
    python -m src.eda
    python -m src.eda --in data/processed/fact_incidencias.csv --out_figs reports/figs --out_maps reports/mapas
    python -m src.eda --no-maps
"""

from __future__ import annotations
import argparse
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Mapas (opcionales, controlados por flag --no-maps)
try:
    import folium
    from folium.plugins import HeatMap
except Exception:  # pragma: no cover
    folium = None
    HeatMap = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = PROJECT_ROOT / "data" / "processed" / "fact_incidencias.csv"
DEFAULT_FIGS = PROJECT_ROOT / "reports" / "figs"
DEFAULT_MAPS = PROJECT_ROOT / "reports" / "mapas"


# ---------- utilidades ----------
def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def savefig(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def month_cat(series_num: pd.Series) -> pd.Categorical:
    meses_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    idx = series_num.clip(1, 12).astype(int) - 1
    return pd.Categorical([meses_es[i] for i in idx], categories=meses_es, ordered=True)


# ---------- carga ----------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el CSV de entrada: {path}")
    df = pd.read_csv(path, encoding="utf-8")
    # Tipos seguros mínimos
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    for col in ["Tiempo_Respuesta_min", "Distancia_km", "Costo_EUR", "Latitud", "Longitud", "Satisfaccion_1a5"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # SLA a entero si existe
    if "SLA_Incumplido" in df.columns:
        df["SLA_Incumplido"] = pd.to_numeric(df["SLA_Incumplido"], errors="coerce").astype("Int64")
    return df


# ---------- figuras ----------
def fig_hist_tiempo(df: pd.DataFrame, outdir: Path) -> None:
    if "Tiempo_Respuesta_min" not in df.columns:
        return
    warnings.filterwarnings("ignore", category=UserWarning)
    sns.set(style="whitegrid")
    x = df["Tiempo_Respuesta_min"].dropna()
    if x.empty:
        return
    p95 = x.quantile(0.95)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(x[x <= p95], bins=30, kde=True, ax=ax)
    ax.set_title("Distribución del Tiempo de Respuesta (<= p95)")
    ax.set_xlabel("Tiempo de Respuesta (min)")
    savefig(fig, outdir / "hist_tiempo_respuesta.png")


def fig_box_coste_por_tipo(df: pd.DataFrame, outdir: Path) -> None:
    if not {"Costo_EUR", "Tipo_Incidencia"}.issubset(df.columns):
        return
    sns.set(style="whitegrid")
    d = df[["Costo_EUR", "Tipo_Incidencia"]].dropna().copy()
    if d.empty:
        return
    p98 = d["Costo_EUR"].quantile(0.98)
    d = d[d["Costo_EUR"] <= p98]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=d, x="Costo_EUR", y="Tipo_Incidencia", showfliers=False, ax=ax)
    sns.stripplot(data=d, x="Costo_EUR", y="Tipo_Incidencia", color="k", size=2, alpha=0.25, ax=ax)
    ax.set_title("Costo por Tipo de Incidencia (recorte p98)")
    ax.set_xlabel("Costo (€)")
    ax.set_ylabel("")
    savefig(fig, outdir / "box_costo_por_tipo.png")


def fig_barras_ciudad(df: pd.DataFrame, outdir: Path, top_n: int = 15) -> None:
    if "Ciudad" not in df.columns:
        return
    sns.set(style="whitegrid")
    conteo = df["Ciudad"].dropna().value_counts().head(top_n)
    if conteo.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=conteo.values, y=conteo.index, ax=ax)
    ax.set_title(f"Incidencias por Ciudad (Top {top_n})")
    ax.set_xlabel("Incidencias")
    ax.set_ylabel("Ciudad")
    savefig(fig, outdir / "barras_incidencias_ciudad_top.png")


def fig_serie_mensual(df: pd.DataFrame, outdir: Path) -> None:
    if "Fecha" not in df.columns:
        return
    d = df.dropna(subset=["Fecha"]).copy()
    if d.empty:
        return
    d["Anio"] = d["Fecha"].dt.year
    d["MesN"] = d["Fecha"].dt.month
    d["Mes"] = month_cat(d["MesN"])
    serie = (d.groupby(["Anio", "Mes"]).size().rename("Incidencias").reset_index())
    if serie.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=serie, x="Mes", y="Incidencias", hue="Anio", marker="o", ax=ax)
    ax.set_title("Incidencias por Mes y Año")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Incidencias")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Año")
    savefig(fig, outdir / "linea_incidencias_mes_anio.png")


def fig_corr_numericas(df: pd.DataFrame, outdir: Path) -> None:
    num = df.select_dtypes(include=["number"])
    if num.shape[1] < 2:
        return
    corr = num.corr()
    order = corr.abs().sum().sort_values(ascending=False).index
    corr = corr.loc[order, order]
    mask = corr.abs() < 0.5  # oculta correlaciones débiles
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, cbar_kws={"shrink": .8}, mask=mask, ax=ax)
    ax.set_title("Matriz de Correlación (|r| ≥ 0.5)")
    savefig(fig, outdir / "heatmap_correlacion.png")


def fig_sla_rate_ciudad(df: pd.DataFrame, outdir: Path, top_n: int = 15) -> None:
    if not {"Ciudad", "SLA_Incumplido"}.issubset(df.columns):
        return
    d = df[["Ciudad", "SLA_Incumplido"]].dropna().copy()
    if d.empty:
        return
    tasa = (d.groupby("Ciudad")["SLA_Incumplido"].mean().mul(100).sort_values(ascending=False).head(top_n))
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=tasa.values, y=tasa.index, ax=ax)
    ax.set_title(f"% Incumplimiento SLA por Ciudad (Top {top_n})")
    ax.set_xlabel("% Incumple SLA")
    ax.set_ylabel("Ciudad")
    savefig(fig, outdir / "barras_sla_por_ciudad_top.png")


def build_maps(df: pd.DataFrame, outdir: Path) -> None:
    if folium is None or HeatMap is None:
        print("[WARN] folium no disponible: omitiendo mapas.")
        return
    if not {"Latitud", "Longitud"}.issubset(df.columns):
        return
    d = df.dropna(subset=["Latitud", "Longitud"]).copy()
    if d.empty:
        return

    # Centro aproximado de España
    center = [40.4168, -3.7038]
    m = folium.Map(location=center, zoom_start=5, tiles="cartodbpositron")

    # Heatmap por densidad de incidencias
    heat_data = d[["Latitud", "Longitud"]].values.tolist()
    if len(heat_data) > 0:
        HeatMap(heat_data, min_opacity=0.3, radius=10, blur=15).add_to(m)

    out_html = outdir / "mapa_incidencias.html"
    m.save(str(out_html))
    print(f"[OK] Mapa guardado en {out_html}")


# ---------- CLI ----------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EDA Asistencia Carretera (figuras y mapas)")
    p.add_argument("--in", dest="input_csv", default=str(DEFAULT_IN),
                   help="Ruta al CSV procesado (por defecto: data/processed/fact_incidencias.csv)")
    p.add_argument("--out_figs", dest="out_figs", default=str(DEFAULT_FIGS),
                   help="Directorio de salida para figuras PNG (por defecto: reports/figs)")
    p.add_argument("--out_maps", dest="out_maps", default=str(DEFAULT_MAPS),
                   help="Directorio de salida para mapas HTML (por defecto: reports/mapas)")
    p.add_argument("--no-maps", action="store_true",
                   help="Si se indica, no genera mapas de folium")
    p.add_argument("--top-cities", type=int, default=15,
                   help="Top N ciudades para las gráficas de barras (por defecto: 15)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_path = Path(args.input_csv)
    out_figs = Path(args.out_figs)
    out_maps = Path(args.out_maps)
    ensure_dir(out_figs)
    ensure_dir(out_maps)

    print(f"[INFO] Leyendo: {in_path}")
    df = load_data(in_path)

    print("[INFO] Generando figuras…")
    fig_hist_tiempo(df, out_figs)
    fig_box_coste_por_tipo(df, out_figs)
    fig_barras_ciudad(df, out_figs, top_n=args.top_cities)
    fig_serie_mensual(df, out_figs)
    fig_corr_numericas(df, out_figs)
    fig_sla_rate_ciudad(df, out_figs, top_n=args.top_cities)
    print(f"[OK] Figuras en: {out_figs}")

    if not args.no_maps:
        print("[INFO] Generando mapa…")
        build_maps(df, out_maps)
    else:
        print("[INFO] Mapas desactivados (--no-maps).")

    print("[DONE] EDA completado.")


if __name__ == "__main__":
    main()
