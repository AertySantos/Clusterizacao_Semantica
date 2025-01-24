# Variáveis
PYTHON = python
SCRIPT = main_clustering.py
DATASET = dataset.txt
INPUT_PATH = ./data/input/
OUTPUT_PATH = ./data/output/
FORMAT = dense

# Parâmetros
DISTANCES = euclidean manhattan cosine cityblock l1 l2
ALGORITHMS = kmeans agglomerative dbscan spectral
EVALUATIONS = silhouette ch_score db_score sse

# Geração de combinações
COMBINATIONS = $(foreach dist,$(DISTANCES),$(foreach alg,$(ALGORITHMS),$(foreach eval,$(EVALUATIONS),$(dist)-$(alg)-$(eval))))

# Alvo principal: executa todas as combinações
all: $(foreach dist,$(DISTANCES),$(foreach alg,$(ALGORITHMS),$(foreach eval,$(EVALUATIONS),run-$(dist)-$(alg)-$(eval))))

# Exibe as combinações disponíveis
list:
	@echo "Use 'make N' onde N é o número da combinação desejada."
	@echo "Combinações disponíveis:"
	@$(foreach idx, $(shell seq 1 $(words $(COMBINATIONS))), echo "$(idx): $(word $(idx),$(COMBINATIONS))";)

# Regras para executar cada combinação individualmente
$(foreach idx, $(shell seq 1 $(words $(COMBINATIONS))), $(eval $(idx): run-$(word $(idx),$(COMBINATIONS))))

# Regra genérica para executar combinações
run-%:
	@combination=$*; \
	dist=$$(echo $$combination | cut -d- -f1); \
	alg=$$(echo $$combination | cut -d- -f2); \
	eval=$$(echo $$combination | cut -d- -f3); \
	echo "Executando: Distância=$$dist, Algoritmo=$$alg, Avaliação=$$eval"; \
	$(PYTHON) $(SCRIPT) $(DATASET) \
		-i $(INPUT_PATH) \
		-o $(OUTPUT_PATH) \
		-f $(FORMAT) \
		-d $$dist \
		-a $$alg \
		-e $$eval \
		|| echo "Erro com a combinação: $$combination"

# Limpa os arquivos de saída
clean:
	rm -f $(OUTPUT_PATH)clusters.txt $(OUTPUT_PATH)exec.csv $(OUTPUT_PATH)exceptions.csv
	@echo "Arquivos de saída limpos."

