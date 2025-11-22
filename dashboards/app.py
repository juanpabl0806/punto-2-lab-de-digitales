import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Prevención de STC", layout="wide")

@st.cache_data
def load_data():
    path = Path("data/processed/dataset_analitico.parquet")
    if path.exists():
        return pd.read_parquet(path)
    else:
        st.warning("Ejecuta `make etl` para generar el dataset procesado.")
        return pd.DataFrame()

df = load_data()
st.title("Sistema de prevención del síndrome de túnel carpiano")

if df.empty:
    st.stop()

# Filtros
col1, col2, col3, col4 = st.columns(4)
with col1:
    sexo = st.multiselect("Sexo", options=sorted(df["sexo"].dropna().unique()))
with col2:
    ocup = st.multiselect("Ocupación", options=sorted(df["ocupación"].dropna().unique()))
with col3:
    riesgo = st.multiselect("Riesgo", options=["bajo", "medio", "alto"])
with col4:
    rango_edad = st.slider("Rango de edad", int(df["edad"].min()), int(df["edad"].max()),
                           (int(df["edad"].min()), int(df["edad"].max())))

q = df.copy()
if sexo: q = q[q["sexo"].isin(sexo)]
if ocup: q = q[q["ocupación"].isin(ocup)]
if riesgo: q = q[q["riesgo_label"].isin(riesgo)]
q = q[(q["edad"] >= rango_edad[0]) & (q["edad"] <= rango_edad[1])]

st.subheader("Resumen")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Registros", f"{len(q):,}")
m2.metric("Riesgo alto (%)", f"{(q['riesgo_label']=='alto').mean()*100:,.1f}%")
m3.metric("IER promedio", f"{q['IER'].mean():.2f}")
m4.metric("Latencia EMG (ms) mediana", f"{q['latencia_ms'].median():.2f}")

st.subheader("Distribución de riesgo")
fig_risk = px.histogram(q, x="riesgo_score", color="riesgo_label", nbins=30)
st.plotly_chart(fig_risk, use_container_width=True)

st.subheader("Factores clave")
c1, c2 = st.columns(2)
with c1:
    fig_ier = px.scatter(q, x="repetitividad", y="IER", color="riesgo_label",
                         trendline="lowess", labels={"IER":"Índice de exposición repetitiva"})
    st.plotly_chart(fig_ier, use_container_width=True)
with c2:
    fig_emg = px.scatter(q, x="latencia_ms", y="velocidad_conducción_m_s", color="riesgo_label",
                         labels={"latencia_ms":"Latencia (ms)", "velocidad_conducción_m_s":"Vel. conducción (m/s)"})
    st.plotly_chart(fig_emg, use_container_width=True)

st.subheader("Comparación por ocupación")
fig_box = px.box(q, x="ocupación", y="riesgo_score", color="ocupación")
st.plotly_chart(fig_box, use_container_width=True)

st.caption("Datos generados por pipeline ETL. Ajustar umbrales en config/etl.yaml.")
