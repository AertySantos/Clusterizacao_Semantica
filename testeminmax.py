import pandas as pd

# Exemplo de DataFrame
data = {
    'col1': [10, 20, 30, 40, 50],
    'col2': [100, 200, 300, 400, 500]
}
df = pd.DataFrame(data)

# Aplicando a normalização Min-Max
df_normalized = (df - df.min()) / (df.max() - df.min())

print(df_normalized)

