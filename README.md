# IA - TaxiGreen: Sistema de Gestão Inteligente de Frota

Sistema de simulação e gestão de uma frota inteligente, **TaxiGreen**, implementando algoritmos de procura informada e não informada para otimizar a alocação de veículos.

---

## Como Executar

Abre a interface gráfica com janelas de configuração:

```bash
make run
```

### Executar testes

##### Todos os testes
```bash
make test
```

##### Testes específicos
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

### Diagnóstico

Executa diagnóstico detalhado do sistema de trânsito dinâmico.

```bash
make diagnostico
```

---

## Contribuidores

a106853 | Ana Beatriz Ribeiro Freitas

a107365 | Beatriz Martins Miranda

a106877 | José Miguel Fernandes Cação

a106793 | Lucas André Dias Fernandes
