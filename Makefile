# Makefile para Projeto TaxiGreen
# Inteligência Artificial - Universidade do Minho

.PHONY: all
all: help

.PHONY: help
help:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║          TaxiGreen - Sistema de Gestão de Frota        ║"
	@echo "║              Inteligência Artificial - UM              ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Comandos Disponíveis:"
	@echo ""
	@echo " make run               		- Executa simulação principal"
	@echo " make test              		- Executa todos os testes"
	@echo " make compare-algoritmos     - Compara algoritmos"
	@echo " make compare-strategies     - Compara estratégias de seleção"
	@echo " make clean         			- Limpa arquivos temporários"
	@echo ""

# ==================== EXECUÇÃO ====================

.PHONY: run
run:
	@echo "Executando simulação TaxiGreen..."
	python3 taxigreen.py


# ==================== TESTES ====================

.PHONY: test
test:
	@echo " Executando TODOS os testes..."
	python3 executar_testes.py

.PHONY: compare-algoritmos
compare-algoritmos:
	@echo "Comparando algoritmos de procura..."
	python3 testes/algoritmos/testar_algoritmos.py

.PHONY: compare-strategies
compare-strategies:
	@echo "Comparando estratégias de seleção..."
	python3 testes/integracao/test_estrategias_selecao.py

.PHONY: diagnostico
diagnostico:
	@echo "Diagnóstico do sistema de trânsito..."
	python3 diagnostico_transito.py
	
# ==================== BENCHMARKS ====================
# todo : verificar se vale a pena

.PHONY: benchmark
benchmark:
	@echo "$(COLOR_YELLOW)⚡ Executando benchmarks de performance...$(COLOR_RESET)"
	$(PYTHON) $(TEST_DIR)/desempenho/benchmark_algoritmos.py

.PHONY: benchmark-cache
benchmark-cache:
	@echo "$(COLOR_YELLOW)⚡ Benchmarking sistema de cache...$(COLOR_RESET)"
	$(PYTHON) $(TEST_DIR)/desempenho/benchmark_cache.py

.PHONY: stress-test
stress-test:
	@echo "$(COLOR_RED)🔥 Executando stress test da frota...$(COLOR_RESET)"
	$(PYTHON) $(TEST_DIR)/desempenho/stress_test_frota.py



# ==================== TESTES ESPECÍFICOS ====================

.PHONY: test-transito
test-transito:
	@echo "Testando sistema de trânsito dinâmico..."
	python3 -m unittest testes/integracao/test_transito_dinamico.py -v

.PHONY: test-falhas
test-falhas:
	@echo " Testando sistema de falhas..."
	python3 -m unittest dir/integracao/test_gestor_falhas.py -v

.PHONY: test-ride-sharing
test-ride-sharing:
	@echo "Testando sistema de ride-sharing..."
	python3 -m unittest dir/integracao/test_ride_sharing.py -v


# ==================== LIMPEZA ====================

.PHONY: clean
clean:
	@echo " Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	@echo "✓ Limpeza concluída!"
