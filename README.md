# TaxiGreen — Sistema de Gestão de Frota

Projeto desenvolvido no âmbito da unidade curricular **Inteligência Artificial** (3º ano, 1º semestre 2024/2025) da **Universidade do Minho**. Simulação e gestão de uma frota (TaxiGreen), com componentes de **procura/planeamento**, **trânsito dinâmico**, **ride-sharing**, **gestão de falhas** e uma **suite de testes** organizada. Inclui um **Makefile** com atalhos para executar simulações, diagnósticos e testes.

Desenvolvimento de algoritmos de procura informada e não informada para otimizar a gestão de uma frota de táxis mista (veículos elétricos e a combustão), maximizando a eficiência operacional, reduzindo custos energéticos e cumprindo critérios ambientais. O sistema procura equilibrar a alocação de veículos com diferentes características — **autonomia, capacidade e custos operacionais** — adaptando-se a condições dinâmicas como **procura variável, trânsito e recarga de veículos**. A cidade é representada como um **grafo**, e são testadas várias estratégias de procura para determinar a mais eficiente.

## Como executar

Para ver os comandos disponíveis:

```bash
make help
```

Comandos principais:

- Executar a simulação principal:

```bash
make run
```

- Executar todos os testes (runner do projeto):

```bash
make test
```

- Comparar algoritmos de procura:

```bash
make compare-algoritmos
```

- Comparar estratégias de seleção:

```bash
make compare-strategies
```

- Executar diagnóstico do trânsito dinâmico:

```bash
make diagnostico
```

---

### Contribuidores

a106853 | Ana Beatriz Ribeiro Freitas

a107365 | Beatriz Martins Miranda

a106877 | José Miguel Fernandes Cação

a106793 | Lucas André Dias Fernandes
