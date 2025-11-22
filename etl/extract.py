import pandas as pd
from .utils import load_config

def extract():
    cfg = load_config()
    base = cfg["paths"]["raw_dir"]
    df_pac = pd.read_csv(f'{base}/{cfg["files"]["pacientes"]}')
    df_eval = pd.read_csv(f'{base}/{cfg["files"]["evaluaciones"]}', parse_dates=["fecha"])
    df_erg = pd.read_csv(f'{base}/{cfg["files"]["ergonomia"]}')
    df_emg = pd.read_csv(f'{base}/{cfg["files"]["emg"]}')
    df_hab = pd.read_csv(f'{base}/{cfg["files"]["hábitos"]}')
    return df_pac, df_eval, df_erg, df_emg, df_hab
