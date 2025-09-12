"""
ETL del proyecto Asistencia Carretera.
- Lee el CSV crudo desde data/raw/incidencias_asistencia.csv (por defecto).
- Limpia/estandariza columnas (fechas, numéricos, textos).
- Crea target SLA_Incumplido (0/1) a partir de "Sí/No" o, si falta, por umbral de 45 min.
- Exporta:
    - data/processed/fact_incidencias.csv
    - data/processed/incidencias_mes.csv
    - data/processed/sla_por_ciudad.csv
    - data/processed/sla_por_proveedor.csv
    - data/processed/costo_por_tipo.csv
Uso:
    python -m src.etl
    python -m src.etl --in data/raw/incidencias_asistencia.csv --out data/processed
"""

from __future__ import annotations
import argparse
from pathlib import Path
import unicodedata
import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def norm_txt(s: object) -> str:
    """Normaliza strings: sin tildes, minúsculas, sin espacios extremos."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.strip().lower()


def ensure_dirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    return df


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # -- quitar 'Notas' si existe
    if "Notas" in df.columns:
        df = df.drop(columns=["Notas"])

    # -- fechas / horas
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    if "Hora" in df.columns:
        # Mantener como texto normalizado HH:MM:SS si viene HH:MM
        df["Hora"] = pd.to_datetime(df["Hora"], errors="coerce").dt.time

    # Fecha_Hora (si no existe o si tiene NaN)
    if "Fecha_Hora" not in df.columns or df["Fecha_Hora"].isna().any():
        if "Fecha" in df.columns and "Hora" in df.columns:
            df["Fecha_Hora"] = pd.to_datetime(
                df["Fecha"].astype(str) + " " + df["Hora"].astype(str),
                errors="coerce",
            )
        elif "Fecha" in df.columns:
            df["Fecha_Hora"] = pd.to_datetime(df["Fecha"], errors="coerce")

    # -- numéricos clave
    for col in [
        "Distancia_km",
        "Tiempo_Respuesta_min",
        "Costo_EUR",
        "Latitud",
        "Longitud",
        "Satisfaccion_1a5",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -- textos clave
    for col in ["Ciudad", "Proveedor", "Tipo_Incidencia", "Medio_Retorno", "Resuelto"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # -- SLA_Incumplido (0/1) desde "Sí/No" si existe; si no, por umbral >45
    if "SLA_45min_Incumplido" in df.columns:
        tmp = df["SLA_45min_Incumplido"].map(norm_txt).map({"si": 1, "no": 0})
        if tmp.notna().any():
            df["SLA_Incumplido"] = tmp.astype("Int64")
        else:
            # fallback al cálculo por umbral
            df["SLA_Incumplido"] = (df["Tiempo_Respuesta_min"] > 45).astype("Int64")
    else:
        df["SLA_Incumplido"] = (df["Tiempo_Respuesta_min"] > 45).astype("Int64")

    # -- columnas calendario
    if "Fecha" in df.columns:
        df["Anio"] = df["Fecha"].dt.year
        df["MesN"] = df["Fecha"].dt.month
        meses_es = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
        }
        df["Mes"] = df["MesN"].map(meses_es)

    return df


def export_processed(df: pd.DataFrame, out_dir: Path, save_aux: bool = True) -> None:
    ensure_dirs(out_dir)

    # Fact base para BI
    cols_base = [
        "Fecha", "Fecha_Hora", "Ciudad", "Proveedor", "Tipo_Incidencia",
        "Distancia_km", "Tiempo_Respuesta_min", "Costo_EUR", "Satisfaccion_1a5",
        "SLA_Incumplido", "Latitud", "Longitud", "Anio", "MesN", "Mes",
    ]
    cols_base = [c for c in cols_base if c in df.columns]
    fact = df[cols_base].copy()

    fact_path = out_dir / "fact_incidencias.csv"
    fact.to_csv(fact_path, index=False, encoding="utf-8")
    print(f"[OK] Guardado: {fact_path}")

    if not save_aux:
        return

    # Auxiliares
    if {"Anio", "MesN", "Mes"}.issubset(fact.columns):
        incidencias_mes = (
            fact.groupby(["Anio", "MesN", "Mes"], dropna=False)
            .size()
            .rename("Incidencias")
            .reset_index()
            .sort_values(["Anio", "MesN"])
        )
        p = out_dir / "incidencias_mes.csv"
        incidencias_mes.to_csv(p, index=False, encoding="utf-8")
        print(f"[OK] Guardado: {p}")

    if "Ciudad" in fact.columns and "SLA_Incumplido" in fact.columns:
        sla_ciudad = (
            fact.groupby("Ciudad")["SLA_Incumplido"]
            .agg(Incumple_pct="mean", n="count")
            .reset_index()
        )
        sla_ciudad["Incumple_pct"] = (sla_ciudad["Incumple_pct"] * 100).round(1)
        p = out_dir / "sla_por_ciudad.csv"
        sla_ciudad.to_csv(p, index=False, encoding="utf-8")
        print(f"[OK] Guardado: {p}")

    if "Proveedor" in fact.columns and "SLA_Incumplido" in fact.columns:
        sla_prov = (
            fact.groupby("Proveedor")["SLA_Incumplido"]
            .agg(Incumple_pct="mean", n="count")
            .reset_index()
        )
        sla_prov["Incumple_pct"] = (sla_prov["Incumple_pct"] * 100).round(1)
        p = out_dir / "sla_por_proveedor.csv"
        sla_prov.to_csv(p, index=False, encoding="utf-8")
        print(f"[OK] Guardado: {p}")

    if "Tipo_Incidencia" in fact.columns and "Costo_EUR" in fact.columns:
        costo_tipo = (
            fact.groupby("Tipo_Incidencia")["Costo_EUR"]
            .agg(count="count", mean="mean", median="median", std="std")
            .reset_index()
            .sort_values("mean", ascending=False)
        )
        p = out_dir / "costo_por_tipo.csv"
        costo_tipo.to_csv(p, index=False, encoding="utf-8")
        print(f"[OK] Guardado: {p}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ETL Asistencia Carretera")
    parser.add_argument(
        "--in", dest="input_csv",
        default=str(PROJECT_ROOT / "data" / "raw" / "incidencias_asistencia.csv"),
        help="Ruta al CSV crudo (por defecto: data/raw/incidencias_asistencia.csv)"
    )
    parser.add_argument(
        "--out", dest="out_dir",
        default=str(PROJECT_ROOT / "data" / "processed"),
        help="Directorio de salida (por defecto: data/processed)"
    )
    parser.add_argument(
        "--no-aux", action="store_true",
        help="Si se indica, no exporta tablas auxiliares"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_csv = Path(args.input_csv)
    out_dir = Path(args.out_dir)

    if not input_csv.exists():
        raise FileNotFoundError(f"No se encontró el CSV de entrada: {input_csv}")

    print(f"[INFO] Leyendo: {input_csv}")
    df = load_raw(input_csv)

    print("[INFO] Limpiando/transformando…")
    df = clean_df(df)

    print(f"[INFO] Exportando a: {out_dir}")
    export_processed(df, out_dir, save_aux=not args.no_aux)

    print("[DONE] ETL completado.")


if __name__ == "__main__":
    main()
