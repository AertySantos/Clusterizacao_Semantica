from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd

# Exemplo de DataFrame
data = {'coluna1': ['texto exemplo A', 'outro exemplo B'],
        'coluna2': ['frase X', 'frase Y']}
df = pd.DataFrame(data)

# Carregar o modelo e o tokenizer
model_name = 'bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def gerar_embedding(texto):
    # Tokenização
    tokens = tokenizer(texto, return_tensors='pt', padding=True, truncation=True, max_length=128)
    # Gerar embedding
    with torch.no_grad():
        output = model(**tokens)
    # Usar o vetor CLS como embedding
    return output.last_hidden_state[:, 0, :].squeeze().numpy()

# Aplicar a função a cada coluna e armazenar os embeddings
df['coluna1_embedding'] = df['coluna1'].apply(gerar_embedding)
df['coluna2_embedding'] = df['coluna2'].apply(gerar_embedding)

print(df)



