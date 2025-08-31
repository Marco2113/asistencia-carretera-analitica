import streamlit as st
import pandas as pd

st.set_page_config(page_title="Asistencia en Carretera - Incidencias", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("incidencias_asistencia_carretera.csv")

df = load_data()

st.title("Asistencia en Carretera – Análisis de Incidencias")
st.caption("Dataset sintético para portfolio.")

# Filtros
cols = st.columns(4)
with cols[0]:
    ciudad = st.multiselect("Ciudad", sorted(df['Ciudad'].unique().tolist()))
with cols[1]:
    tipo = st.multiselect("Tipo de Incidencia", sorted(df['Tipo_Incidencia'].unique().tolist()))
with cols[2]:
    medio = st.multiselect("Medio de Retorno", sorted(df['Medio_Retorno'].unique().tolist()))
with cols[3]:
    resuelto = st.multiselect("Resuelto", ["Sí","No"])

fdf = df.copy()
if ciudad: fdf = fdf[fdf['Ciudad'].isin(ciudad)]
if tipo: fdf = fdf[fdf['Tipo_Incidencia'].isin(tipo)]
if medio: fdf = fdf[fdf['Medio_Retorno'].isin(medio)]
if resuelto: fdf = fdf[fdf['Resuelto'].isin(resuelto)]

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Incidencias", f"{len(fdf):,}")
k2.metric("Tiempo medio (min)", f"{fdf['Tiempo_Respuesta_min'].mean():.1f}")
sla_pct = (fdf['SLA_45min_Incumplido'].eq('Sí').mean()*100) if len(fdf) else 0
k3.metric("SLA incumplido", f"{sla_pct:.1f}%")
k4.metric("Coste medio (€)", f"{fdf['Costo_EUR'].mean():.2f}")
k5.metric("Satisfacción media", f"{fdf['Satisfaccion_1a5'].mean():.2f}")

# Tablas resumidas
st.subheader("Incidencias por ciudad / tipo")
c1, c2 = st.columns(2)
with c1:
    st.dataframe(fdf.groupby('Ciudad').size().reset_index(name='Incidencias').sort_values('Incidencias', ascending=False), use_container_width=True)
with c2:
    st.dataframe(fdf.groupby('Tipo_Incidencia').size().reset_index(name='Incidencias').sort_values('Incidencias', ascending=False), use_container_width=True)

st.subheader("Coste medio por Tipo de Incidencia")
st.dataframe(fdf.groupby('Tipo_Incidencia')['Costo_EUR'].mean().reset_index().sort_values('Costo_EUR', ascending=False), use_container_width=True)

st.subheader("Vista de datos")
st.dataframe(fdf.head(200), use_container_width=True)
