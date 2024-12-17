import numpy as np

data = []

docs = []
with open("data/IN/dataset.txt", 'r') as fh:
        docs = fh.read().split('\n')    

fsep = " "  # Usando espaço como separador

data = np.array(
                [
                    [float(value.replace("\t", " ").strip()) for value in line.split(fsep)] 
                    for line in docs if line.strip()
                ]
            )
print(data)


