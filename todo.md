| Categoria                                     | O que falta                                                                                                                                            |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Formulação do problema de procura** | Definir o estado (posição dos veículos, pedidos pendentes, autonomia, etc.), operadores (mover, atender pedido, recarregar), teste objetivo, custo. |
| **Algoritmos de procura**               | Implementar e comparar estratégias (BFS, UCS, A*, Greedy, etc.).                                                                                      |
| **Simulação dinâmica**               | Geração aleatória de pedidos ao longo do tempo, atualização da frota, recargas, falhas, etc.                                                      |
| **Métricas de desempenho**             | Tempo médio de resposta, custos operacionais, emissões CO₂, km em vazio, etc.                                                                       |
| **Gestor de Frota**                     | Um módulo que coordena veículos e pedidos (atribui pedidos, monitoriza estados).                                                                     |
| **Relatório final**                    | Descrição, formulação, resultados, discussão.                                                                                                     |

Encontrar a melhor sequência de ações (movimentos e atribuições) que minimize o **custo total de operação** e o  **tempo médio de resposta** , garantindo que todos os pedidos válidos sejam atendidos dentro das restrições (autonomia, capacidade, disponibilidade, preferências ambientais).

Mas o enunciado encoraja uma  **função composta** , ponderando:

* custo de operação (€/km)
* penalização pelo tempo de espera do cliente
* penalização ambiental (emissões de CO₂)
* penalização por pedidos rejeitados


# TODO List Completo - TaxiGreen

## 🔴 **CRÍTICO - Requisitos Fundamentais em Falta**

### 1. **Formulação Formal do Problema de Procura**

* [ ] Documentar **Estado Inicial** (posição veículos, autonomia, pedidos pendentes)
* [ ] Definir **Teste Objetivo** (todos pedidos atendidos? tempo máximo? custo mínimo?)
* [ ] Especificar **Operadores/Ações** (mover, recarregar, abastecer, atribuir pedido)
* [ ] Formalizar **Função de Custo** (tempo + distância + emissões + custos operacionais)

### 2. **Sistema de Priorização de Pedidos**

* [ ] Implementar lógica de **pedidos urgentes/premium** (atualmente só existe campo `prioridade` mas não é usado efetivamente)
* [ ] Criar sistema de **tempo de espera máximo** por pedido
* [ ] Implementar **penalização** por pedidos não atendidos no tempo

### 3. **Gestão de Autonomia e Recargas**

* [ ] **Planeamento proativo de recargas** - veículos devem ir recarregar ANTES de ficar sem autonomia
* [ ] Implementar rota com checkpoint de recarga/abastecimento (usar `bfs_com_checkpoint` já existente)
* [ ] Adicionar lógica de **recarga parcial** (não sempre 100%)
* [ ] Implementar **tempo de recarga/abastecimento** afetando disponibilidade do veículo
* [ ] Adicionar **fila de espera** em estações de recarga ocupadas

### 4. **Otimização de Rotas**

* [ ] Minimizar **km sem passageiros** (dead mileage)
* [ ] Implementar **agrupamento de pedidos** próximos geograficamente
* [ ] Considerar **proximidade entre destino atual e novo pedido** na seleção de veículo

## 🟠 **IMPORTANTE - Funcionalidades Core**

### 5. **Métricas de Avaliação**

* [ ] **Taxa de ocupação da frota** (% tempo com passageiros vs disponível)
* [ ] **Km percorridos sem passageiros** (já tem `km_total` mas não distingue)
* [ ] **Tempo médio de resposta** (tempo entre pedido e início do serviço)
* [ ] **Emissões CO2 por pedido/por km**
* [ ] **Custo por pedido** vs **receita** (falta modelar receita!)
* [ ] Gráficos/visualização das métricas ao longo do tempo

### 6. **Condições Dinâmicas - Trânsito**

* [ ] Adicionar campo `congestion` em `Aresta` (já comentado no código)
* [ ] Variação de trânsito por **hora do dia** (rush hour)
* [ ] Variação de trânsito por **zona** (centro vs periferia)
* [ ] Recalcular rotas dinamicamente quando trânsito muda

### 7. **Condições Dinâmicas - Falhas**

* [ ] Simular **estações de recarga fora de serviço**
* [ ] Simular **veículos em manutenção** (já existe estado `INDISPONIVEL` mas não é usado)
* [ ] Sistema de **roteamento alternativo** quando estação preferida está indisponível

### 8. **Distribuição Geográfica**

* [ ] Implementar **zonas centrais vs periféricas** (adicionar campo em `No`)
* [ ] Aplicar **custos/prioridades diferentes** por zona
* [ ] Criar **padrões de demanda** por zona e hora

### 9. **Sistema de Preferências do Cliente**

* [ ] Validar **preferência ambiental** na atribuição (atualmente há lógica mas aceita "qualquer")
* [ ] Implementar **tempo máximo de espera** por cliente
* [ ] Sistema de **feedback/satisfação** do cliente

## 🟡 **DESEJÁVEL - Melhorias e Extensões**

### 10. **Algoritmos de Procura - Melhorias**

* [ ] Implementar **heurística admissível** em A* que considere:

  * Autonomia restante do veículo
  * Necessidade de recarga no caminho
  * Trânsito esperado
* [ ] Criar **algoritmo híbrido** que escolhe A*/UCS/BFS dependendo da situação
* [ ] Benchmark e **comparação quantitativa** entre algoritmos (tempo execução, nós expandidos, qualidade solução)

### 11. **Predição de Procura**

* [ ] Sistema de **padrões históricos** de pedidos por hora/zona
* [ ] **Posicionamento proativo** de veículos em zonas de alta procura esperada
* [ ] **Previsão de demanda** para próximos N minutos

### 12. **Ride-Sharing**

* [ ] Permitir **múltiplos passageiros** no mesmo veículo (diferentes pedidos)
* [ ] Algoritmo de **matching de pedidos** compatíveis (rotas similares)
* [ ] Gestão de **capacidade dinâmica** (lugares ocupados vs disponíveis)

### 13. **Análise Custo-Benefício Frota Elétrica**

* [ ] Calcular **ROI** (Return on Investment) de veículos elétricos
* [ ] Comparar **custo operacional total** elétrico vs combustão
* [ ] Análise de **breakeven point** da transição para elétricos

### 14. **Integração Meteorológica**

* [ ] Impacto da **chuva na procura** (mais pedidos)
* [ ] Impacto da **chuva no trânsito** (velocidade reduzida)
* [ ] Impacto do **frio na autonomia** dos elétricos

### 15. **Sistema de Incentivos**

* [ ] **Descontos** para clientes que escolhem veículos elétricos
* [ ] **Tarifas dinâmicas** (surge pricing) em horas de pico
* [ ] **Programa de fidelidade** (prioridade para clientes regulares)

### 16. **Otimização de Turnos**

* [ ] Distribuição de veículos ao longo do dia por **turnos**
* [ ] **Rotação de motoristas** (veículos param para descanso)
* [ ] **Planeamento semanal** da operação

## 🔵 **CORREÇÕES E REFINAMENTOS**

### 17. **Bugs e Inconsistências no Código**

* [X] `mover_um_passo()` usa `id_rota` mas deveria ser `indice_rota` (inconsistência)
* [ ] `executar_viagem()` calcula distância direta mas deveria usar rota calculada
* [ ] Falta validação de **rota impossível** (sem caminho entre origem-destino)
* [ ] `selecionar_veiculo_pedido()` usa distância direta mas deveria usar rota otimizada

### 18. **Melhorias na Simulação**

* [ ] Implementar **pausa real** (atualmente só regista evento)
* [ ] Adicionar **velocidade de simulação** ajustável (2x, 5x, 10x)
* [ ] Sistema de **save/load** do estado da simulação
* [ ] **Replay** de simulações anteriores

### 19. **Melhorias na Interface**

* [ ] Mostrar **rota planejada** de cada veículo no mapa (já parcialmente implementado)
* [ ] Adicionar **zoom** e **pan** no mapa
* [ ] Mostrar **estado atual** de cada veículo (hover tooltip)
* [ ] Painel com **comparação de algoritmos** lado a lado
* [ ] **Gráficos em tempo real** das métricas

### 20. **Validação e Testes**

* [ ] Criar **suite de testes unitários** para algoritmos
* [ ] Testes de **casos extremos** (todos veículos sem autonomia, pedidos impossíveis)
* [ ] Validação de **consistência** do grafo (conectividade, nós órfãos)
* [ ] **Benchmark automatizado** com diferentes configurações

## **RELATÓRIO - Requisitos Documentais**

### 21. **Documentação Obrigatória**

* [ ] **Descrição formal do problema** (estado, operadores, objetivo, custo)
* [ ] **Justificação das decisões de design** (estruturas de dados, algoritmos)
* [ ] **Resultados experimentais** com múltiplos cenários
* [ ] **Comparação quantitativa** entre algoritmos (tabelas, gráficos)
* [ ] **Análise crítica** das limitações e trabalho futuro
* [ ] **Avaliação pelos pares** (delta de contribuição)

---

## **Priorização Sugerida**

### **Sprint 1 - Fundação (Crítico para Entrega)**

1. Formulação formal do problema
2. Planeamento proativo de recargas
3. Sistema de priorização de pedidos
4. Métricas completas de avaliação

### **Sprint 2 - Dinâmica (Requisitos do Enunciado)**

5. Condições dinâmicas de trânsito
6. Falhas em estações/veículos
7. Tempo de recarga/abastecimento afetando simulação
8. Correção dos bugs identificados

### **Sprint 3 - Otimização (Diferenciação)**

9. Minimização de km sem passageiros
10. Comparação rigorosa entre algoritmos
11. Ride-sharing básico
12. Posicionamento proativo de veículos

### **Sprint 4 - Extensões (Bônus)**

13. Integração meteorológica
14. Sistema de incentivos
15. Análise custo-benefício frota elétrica
16. Interface avançada com gráficos
