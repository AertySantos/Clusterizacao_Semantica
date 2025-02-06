# Variáveis
PYTHON = python3
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

GRAFICO=$(if $(filter %0 %1 %2 %3 %4 %5 %6 %7 %8 %9 %10,$(MAKECMDGOALS)),TRUE,FALSE)

# Alvo principal: executa todas as combinações com GRAFICO=FALSE
all:
	@for combination in $(COMBINATIONS); do \
		make run-$$combination; \
	done


# Exibe as combinações disponíveis
list:
	@echo "Use 'make N' onde N é o número da combinação desejada."
	@echo "Combinações disponíveis:"
	@$(foreach idx, $(shell seq 1 $(words $(COMBINATIONS))), echo "$(idx): $(word $(idx),$(COMBINATIONS))";)


# Criar regras numéricas para rodar combinações e ativar GRAFICO=TRUE automaticamente
$(foreach idx, $(shell seq 1 $(words $(COMBINATIONS))), \
    $(eval $(idx): run-$(word $(idx),$(COMBINATIONS))))

# Exibe o valor da variável GRAFICO
	
# Regra genérica para executar combinações
run-%:
	
	@echo "Grafico = $(GRAFICO)"
	@combination=$*; \
	dist=$$(echo $$combination | cut -d- -f1); \
	alg=$$(echo $$combination | cut -d- -f2); \
	eval=$$(echo $$combination | cut -d- -f3); \
	grafico=$(GRAFICO); \
	echo "Executando: Distância=$$dist, Algoritmo=$$alg, Avaliação=$$eval, Gráfico=$$grafico"; \
	if [ $$grafico = TRUE ]; then \
		$(PYTHON) $(SCRIPT) $(DATASET) -i $(INPUT_PATH) -o $(OUTPUT_PATH) -f $(FORMAT) -d $$dist -a $$alg -e $$eval -g; \
	else \
		$(PYTHON) $(SCRIPT) $(DATASET) -i $(INPUT_PATH) -o $(OUTPUT_PATH) -f $(FORMAT) -d $$dist -a $$alg -e $$eval; \
	fi

# Limpa os arquivos de saída
clean:
	rm -f $(OUTPUT_PATH)clusters.txt $(OUTPUT_PATH)exec.csv $(OUTPUT_PATH)exceptions.csv
	@echo "Arquivos de saída limpos."
