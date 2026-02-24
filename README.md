# IA - TaxiGreen: Sistema de Gestão Inteligente de Frota

Sistema de simulação e gestão de uma frota inteligente, **TaxiGreen**, implementando algoritmos de procura informada e não informada para otimizar a alocação de veículos.

---

## Como Executar

### Executar a simulação principal

Abre a interface gráfica com janelas de configuração:

```bash
make run
```

### Executar testes

#### Todos os testes
```bash
make test
```

#### Testes específicos
```bash
make test-transito        # Sistema de trânsito dinâmico
make test-falhas          # Sistema de gestão de falhas
make test-ride-sharing    # Sistema de ride-sharing
```

### Análise comparativa

#### Comparar algoritmos de procura
```bash
make compare-algoritmos
```

#### Executar comparador completo
```bash
make comparar
```

#### Comparar estratégias de seleção
```bash
make compare-strategies
```

### 5. Diagnóstico

Executa diagnóstico detalhado do sistema de trânsito dinâmico.

```bash
make diagnostico
```

---

## Algoritmos Implementados

### Procura não informada
- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **UCS** (Uniform Cost Search)

### Procura informada
- **A\*** (A* Search)
- **Greedy** (Greedy Best-First Search)

---

## Estratégias de Seleção de Veículos

- **Menor Distância**: Seleciona o veículo mais próximo
- **Custo Composto**: Considera distância, autonomia e custos
- **Dead Mileage**: Minimiza distância sem passageiro
- **Equilibrada**: Equilibra carga entre veículos
- **Priorizar Elétricos**: Favorece veículos elétricos

---

## Contribuidores

| ID | Nome |
|---|---|
| a106853 | Ana Beatriz Ribeiro Freitas |
| a107365 | Beatriz Martins Miranda |
| a106877 | José Miguel Fernandes Cação |
| a106793 | Lucas André Dias Fernandes |
