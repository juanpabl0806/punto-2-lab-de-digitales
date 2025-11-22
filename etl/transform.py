import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from .utils import load_config

def validate_ranges(df, col, low, high):
    return df[(df[col] >= low) & (df[col] <= high)]

def clean_and_join(df_pac, df_eval, df_erg, df_emg, df_hab):
    cfg = load_config()
    # Validaciones básicas
    df_pac = validate_ranges(df_pac, "edad", *cfg["quality"]["ranges"]["edad"])
    df_emg = validate_ranges(df_emg, "latencia_ms", *cfg["quality"]["ranges"]["latencia_ms"])
    df_emg = validate_ranges(df_emg, "velocidad_conducción_m_s", *cfg["quality"]["ranges"]["velocidad_conducción_m_s"])

    # Deduplicación
    df_pac = df_pac.drop_duplicates(subset=["id_paciente"])
    df_eval = df_eval.drop_duplicates(subset=["id_eval"])
    for d in (df_erg, df_emg, df_hab):
        d.drop_duplicates(inplace=True)

    # Joins por id_eval
    wide = df_eval.merge(df_pac, on="id_paciente", how="left") \
                  .merge(df_erg, on="id_eval", how="left") \
                  .merge(df_emg, on="id_eval", how="left") \
                  .merge(df_hab, on="id_eval", how="left")

    # Imputación simple
    num_cols = wide.select_dtypes(include="number").columns
    wide[num_cols] = wide[num_cols].fillna(wide[num_cols].median())

    # Winsorización ligera
    for c in num_cols:
        q01, q99 = wide[c].quantile([0.01, 0.99])
        wide[c] = np.clip(wide[c], q01, q99)

    # Feature engineering: IER
    wide["IER"] = (wide["repetitividad"] * wide["fuerza_promedio"]) / (1 + wide["pausas_por_hora"])

    # Score riesgo (estandarización y suma)
    risk_components = ["postura_promedio", "IER", "latencia_ms", "severidad_nordic"]
    scaler = StandardScaler()
    z = scaler.fit_transform(wide[risk_components])
    wide["riesgo_score"] = z.sum(axis=1)

    # Etiquetas por terciles
    low_t, med_t = wide["riesgo_score"].quantile([cfg["risk_thresholds"]["low"],
                                                  cfg["risk_thresholds"]["medium"]])
    wide["riesgo_label"] = pd.cut(wide["riesgo_score"],
                                  bins=[-np.inf, low_t, med_t, np.inf],
                                  labels=["bajo", "medio", "alto"])
    return wide

def transform(df_pac, df_eval, df_erg, df_emg, df_hab):
    wide = clean_and_join(df_pac, df_eval, df_erg, df_emg, df_hab)
    return wide
