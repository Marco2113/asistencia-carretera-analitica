#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Estadística descriptiva e inferencial del proyecto.
- Lee data/processed/fact_incidencias.csv (por defecto).
- Calcula:
    * ANOVA + Kruskal de Costo_EUR por Tipo_Incidencia (+ η² y ω²)
    * Chi-cuadrado: Tipo_Incidencia x SLA_Incumplido (+ Cramér's V)
    * Regresión logística (sin fuga): SLA_Incumplido ~ Distancia_km + C(Ciudad)
- Exporta resultados a reports/stats/ (CSV) si se pasa --save.

Uso:
    python -m src.stats
    python -m src.stats --in data/processed/fact_incidencias.csv --save
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ensure_dirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def anova_kru(df: pd.DataFrame) -> dict:
    out = {}

    df = df.copy()
    df = df.dropna(subset=["Costo_EUR", "Tipo_Incidencia"])
    if df.empty:
        return {"msg": "No hay datos válidos para ANOVA/Kruskal."}

    # ANOVA
    groups = [g["Costo_EUR"].dropna().values for _, g in df.groupby("Tipo_Incidencia")]
    f, p = stats.f_oneway(*groups)
    out["anova_F"] = float(f)
    out["anova_p"] = float(p)

    # Efecto (η², ω²) via ANOVA con statsmodels
    m = smf.ols("Costo_EUR ~ C(Tipo_Incidencia)", data=df).fit()
    aov = sm.stats.anova_lm(m, typ=2)
    ss_b = aov.loc["C(Tipo_Incidencia)", "sum_sq"]
    df_b = aov.loc["C(Tipo_Incidencia)", "df"]
    ss_w = aov.loc["Residual", "sum_sq"]
    df_w = aov.loc["Residual", "df"]
    ms_w = ss_w / df_w
    eta2 = ss_b / (ss_b + ss_w)
    omega2 = (ss_b - df_b * ms_w) / (ss_b + ss_w + ms_w)
    out["eta2"] = float(eta2)
    out["omega2"] = float(omega2)

    # Kruskal (no paramétrico)
    h, pkw = stats.kruskal(*groups)
    out["kruskal_H"] = float(h)
    out["kruskal_p"] = float(pkw)

    # Resumen por tipo
    resumen = (
        df.groupby("Tipo_Incidencia")["Costo_EUR"]
        .agg(count="count", mean="mean", median="median", std="std")
        .sort_values("mean", ascending=False)
        .reset_index()
    )
    out["resumen_tipo"] = resumen

    return out


def chi2_sla_tipo(df: pd.DataFrame) -> dict:
    out = {}
    df = df.dropna(subset=["Tipo_Incidencia", "SLA_Incumplido"])
    df["SLA_Incumplido"] = df["SLA_Incumplido"].astype(int)

    tab = pd.crosstab(df["Tipo_Incidencia"], df["SLA_Incumplido"])
    chi2, p, dof, exp = stats.chi2_contingency(tab)
    n = tab.values.sum()
    r, c = tab.shape
    # Cramér's V
    v = np.sqrt(chi2 / (n * (min(r - 1, c - 1))))

    out.update({
        "chi2": float(chi2),
        "p": float(p),
        "dof": int(dof),
        "cramers_v": float(v),
        "min_expected": float(exp.min()),
        "tabla": tab.reset_index(),
    })

    # Tasas de incumplimiento por tipo
    if 1 in tab.columns:
        rate = (tab.get(1, 0) / tab.sum(axis=1)).sort_values(ascending=False)
        out["tasas_incumplimiento"] = rate.reset_index(name="Incumple_%")
    return out


def logistica(df: pd.DataFrame) -> dict:
    """Modelo sin fuga: SLA_Incumplido ~ Distancia_km + C(Ciudad)"""
    out = {}

    cols_needed = ["SLA_Incumplido", "Distancia_km", "Ciudad"]
    dfm = df.dropna(subset=[c for c in cols_needed if c in df.columns]).copy()
    if dfm.empty or not set(cols_needed).issubset(dfm.columns):
        return {"msg": "No hay columnas/datos suficientes para logística."}

    dfm["SLA_Incumplido"] = dfm["SLA_Incumplido"].astype(int)
    dfm["Distancia_km"] = pd.to_numeric(dfm["Distancia_km"], errors="coerce")
    dfm = dfm.dropna(subset=["Distancia_km"])

    # ciudad de referencia
    ref_city = "Madrid" if "Madrid" in dfm["Ciudad"].unique() else dfm["Ciudad"].mode().iat[0]

    formula = f"SLA_Incumplido ~ Distancia_km + C(Ciudad, Treatment(reference='{ref_city}'))"
    model = smf.logit(formula, data=dfm).fit(disp=False)

    params = model.params
    conf = model.conf_int()
    or_table = pd.DataFrame({
        "param": params.index,
        "OR": np.exp(params).values,
        "CI95_inf": np.exp(conf[0]).values,
        "CI95_sup": np.exp(conf[1]).values,
        "p": model.pvalues.values,
    }).round(4)

    # Probabilidad predicha (para export si se desea)
    dfm["Prob_Incumplir"] = model.predict(dfm)

    out["summary"] = model.summary().as_text()
    out["or_table"] = or_table
    out["pred"] = dfm[["Ciudad", "Distancia_km", "SLA_Incumplido", "Prob_Incumplir"]]

    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estadística del proyecto")
    parser.add_argument(
        "--in", dest="input_csv",
        default=str(PROJECT_ROOT / "data" / "processed" / "fact_incidencias.csv"),
        help="Ruta al CSV procesado (por defecto: data/processed/fact_incidencias.csv)"
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Si se indica, guarda resultados en reports/stats/"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_csv = Path(args.input_csv)
    if not input_csv.exists():
        raise FileNotFoundError(f"No se encontró el CSV procesado: {input_csv}")

    print(f"[INFO] Leyendo: {input_csv}")
    df = pd.read_csv(input_csv, encoding="utf-8")

    # ANOVA / Kruskal
    print("[INFO] ANOVA / Kruskal…")
    ak = anova_kru(df)
    if "msg" in ak:
        print("[WARN]", ak["msg"])
    else:
        print(f"ANOVA: F={ak['anova_F']:.3f}, p={ak['anova_p']:.3g}, η²={ak['eta2']:.3f}, ω²={ak['omega2']:.3f}")
        print(f"Kruskal-Wallis: H={ak['kruskal_H']:.3f}, p={ak['kruskal_p']:.3g}")

    # Chi2
    print("[INFO] Chi-cuadrado…")
    c2 = chi2_sla_tipo(df)
    if "msg" in c2:
        print("[WARN]", c2["msg"])
    else:
        print(f"Chi2={c2['chi2']:.2f} | p={c2['p']:.3g} | dof={c2['dof']} | Cramér's V={c2['cramers_v']:.3f}")

    # Logística
    print("[INFO] Regresión logística (sin fuga)…")
    lg = logistica(df)
    if "msg" in lg:
        print("[WARN]", lg["msg"])
    else:
        print(lg["summary"])

    # Guardar
    if args.save:
        out_dir = PROJECT_ROOT / "reports" / "stats"
        ensure_dirs(out_dir)

        if "resumen_tipo" in ak:
            ak["resumen_tipo"].to_csv(out_dir / "costo_por_tipo_resumen.csv", index=False, encoding="utf-8")
        if "tabla" in c2:
            c2["tabla"].to_csv(out_dir / "chi2_tabla_observada.csv", index=False, encoding="utf-8")
        if "tasas_incumplimiento" in c2:
            c2["tasas_incumplimiento"].to_csv(out_dir / "tasas_incumplimiento_por_tipo.csv", index=False, encoding="utf-8")
        if "or_table" in lg:
            lg["or_table"].to_csv(out_dir / "logit_odds_ratios.csv", index=False, encoding="utf-8")
        if "pred" in lg:
            lg["pred"].to_csv(out_dir / "logit_predicciones.csv", index=False, encoding="utf-8")

        print(f"[OK] Resultados guardados en: {out_dir}")

    print("[DONE] Stats completado.")


if __name__ == "__main__":
    main()
