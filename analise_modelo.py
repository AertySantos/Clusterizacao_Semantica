import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Carregar o arquivo
file_path = "data/output/exec.csv"
df = pd.read_csv(file_path, sep="\t")  # Ajuste o separador se necessário

# Remover espaços extras nos nomes das colunas
df.columns = df.columns.str.strip()

# Selecionar métricas relevantes
metrics = ["SS", "DBS", "CHS", "SSE", "CVS"]

# Filtrar apenas linhas com SS ≥ 0
df_filtered = df[df["SS"] >= 0].copy()

# Contar o número de clusters corretamente (baseado nos separadores ":")
df_filtered["Num_Clusters"] = df_filtered["Clusters"].astype(str).apply(lambda x: len(x.split(":")))

# Filtrar apenas algoritmos com mais de 2 clusters
df_filtered = df_filtered[df_filtered["Num_Clusters"] > 4]

if df_filtered.empty:
    print("Nenhuma configuração gerou mais de dois clusters com SS ≥ 0.")
else:
    # Normalizar os dados (SS e CHS devem ser maximizados; DBS e SSE minimizados)
    scaler = MinMaxScaler()
    df_scaled = df_filtered[metrics].copy()
    df_scaled[metrics] = scaler.fit_transform(df_scaled[metrics])

    # Inverter as métricas onde menor é melhor (DBS e SSE)
    for metric in ["DBS", "SSE"]:
        df_scaled[metric] = 1 - df_scaled[metric]

    # Criar um score combinando todas as métricas com pesos opcionais
    weights = {"SS": 1.5, "DBS": 1.5, "CHS": 1.5, "SSE": 1.5, "CVS": 1.5}  # Ajuste os pesos se necessário
    df_scaled["Score"] = sum(df_scaled[metric] * weight for metric, weight in weights.items())

    # Encontrar a melhor linha
    best_index = df_scaled["Score"].idxmax()
    best_row = df_filtered.loc[best_index]  # Pega a linha original, sem normalização

    print("Melhor linha considerando todas as métricas (com SS ≥ 0 e mais de dois clusters):")
    print(best_row)
