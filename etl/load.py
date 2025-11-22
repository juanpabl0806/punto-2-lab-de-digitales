import pandas as pd
from .utils import load_config, ensure_dir

def load(wide: pd.DataFrame):
    cfg = load_config()
    out_dir = cfg["paths"]["processed_dir"]
    ensure_dir(out_dir)
    wide.to_parquet(f"{out_dir}/dataset_analitico.parquet", index=False)
    wide.to_csv(f"{out_dir}/dataset_analitico.csv", index=False)
