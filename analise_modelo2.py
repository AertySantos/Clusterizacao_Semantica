
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

df = pd.read_csv("data/output/exec.csv")
print(df.columns)

# Selecionar apenas as colunas relevantes
metrics = df[["SS", "DBS", "CHS", "SSE"]].copy()

# Normalizar os valores (SS e CHS maximizados, DBS e SSE minimizados)
scaler = MinMaxScaler()
metrics["SS"] = scaler.fit_transform(metrics[["SS"]])  # Quanto maior, melhor
metrics["CHS"] = scaler.fit_transform(metrics[["CHS"]])  # Quanto maior, melhor
metrics["DBS"] = 1 - scaler.fit_transform(metrics[["DBS"]])  # Quanto menor, melhor
metrics["SSE"] = 1 - scaler.fit_transform(metrics[["SSE"]])  # Quanto menor, melhor

# Criar um score combinado (média das métricas normalizadas)
metrics["Score"] = metrics.mean(axis=1)

# Identificar a melhor linha
best_overall_index = metrics["Score"].idxmax()
best_overall = df.loc[best_overall_index]

best_overall