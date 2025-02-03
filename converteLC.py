import pandas as pd
import numpy as np

# Caminho do arquivo
file_path = "data/output/clusters.txt"

# Ler os dados do arquivo
with open(file_path, "r") as file:
    lines = file.readlines()

# Converter os dados para listas de inteiros
data = [list(map(int, line.split())) for line in lines]

df = pd.read_excel("dados.xlsx")

# Criar DataFrame com os vetores como colunas
df2 = pd.DataFrame(data).T  # Transpor para que cada linha vire uma coluna

# Exibir o DataFrame
print(df2.head())

df = pd.concat([df, df2], axis = 1)

df.to_csv("res.csv", index=False, header=True)