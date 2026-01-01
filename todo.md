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

# TODO List Completo - TaxiGreen IA (Análise Final)

## 🟢 **COMPLETO - Já Implementado**

### ✅ Estrutura Base do Projeto

* [X] Modelo de Grafo com nós e arestas (`grafo.py`)
* [X] Representação de tipos de nós (Recolha, Estação Recarga, Posto Abastecimento)
* [X] Sistema de veículos (Elétrico e Combustão) com herança ABC
* [X] Estados de veículos (Disponível, A Servico, Recarregando, etc.) - Enum
* [X] Sistema de pedidos com estados - Enum
* [X] Validações automáticas de pedidos (`__post_init__`)
* [X] Sistema de coordenadas (x, y) para visualização
* [X] Arquitetura modular (modelo/gestão/interface/fabrica)

### ✅ Algoritmos de Procura Implementados

* [X] **A* (A-Estrela)* * - `a_estrela.py`
  * [X] Usa `tempo_real()` considerando trânsito
  * [X] Ignora arestas bloqueadas
  * [X] Heurística euclidiana básica implementada
* [X] **UCS (Uniform Cost Search)** - `ucs.py`
  * [X] Usa `tempo_real()` considerando trânsito
  * [X] Ignora arestas bloqueadas
* [X] **BFS (Breadth-First Search)** - `bfs.py`
  * [X] Procura padrão implementada
  * [X] Variante com checkpoint (`bfs_com_checkpoint`)
* [X] **DFS (Depth-First Search)** - `dfs.py`
  * [X] Procura padrão implementada
* [X] **Funções auxiliares** - `uteis.py`
  * [X] `dist_euclidiana()` - distância euclidiana
  * [X] `tempo_heuristica()` - estimativa de tempo por velocidade média

### ✅ Sistema de Seleção de Algoritmos

* [X] Seleção dinâmica em runtime via `definir_algoritmo_procura()`
* [X] Interface permite alternar entre algoritmos
* [X] Método unificado `calcular_rota()` que delega ao algoritmo escolhido

### ✅ Comparação de Algoritmos

* [X] Sistema completo `ComparadorAlgoritmos` - `comparador_algoritmos.py`
* [X] Métricas: tempo execução, nós expandidos, custo solução
* [X] Relatório em texto formatado
* [X] Relatório em formato dict (para JSON)
* [X] Script de teste independente - `testar_algoritmos.py`

### ✅ Gestão de Frota

* [X] Seleção de veículo por proximidade e capacidade
* [X] Validação de autonomia antes de atribuir
* [X] Filtragem por preferência ambiental (com fallback)
* [X] Cálculo de rotas completas (origem → pickup → destino)
* [X] Sistema de recarga com checkpoint (`atribuir_com_recarga`)
* [X] Verificação proativa de necessidade de recarga (threshold 30%)
* [X] Gestão de múltiplos veículos simultaneamente
* [X] Busca de estação mais próxima disponível
* [X] Validação de disponibilidade de estações antes de recarga

### ✅ Simulação Dinâmica

* [X] Sistema de tempo (minuto a minuto)
* [X] Fila de prioridade para pedidos (heapq por instante + prioridade)
* [X] Agendamento de pedidos por instante
* [X] Movimento passo-a-passo dos veículos (`mover_um_passo`)
* [X] Atualização de estados em tempo real
* [X] Sistema de pausa/retoma da simulação (flag booleana)
* [X] Verificação de conclusão de pedidos por fase (atribuído → em execução → concluído)
* [X] Gestão de tempo de ocupação (`tempo_ocupado_ate`)
* [X] Simulação completa até duração total

### ✅ Condições Dinâmicas - Trânsito

* [X] Sistema completo `GestorTransito` - `transito_dinamico.py`
* [X] Campo `congestion` em Aresta implementado
* [X] Método `tempo_real()` retorna tempo × congestion
* [X] Variação por hora do dia (rush hour, madrugada)
  * [X] Rush manhã (7-10h): 1.8x
  * [X] Hora almoço (12-14h): 1.3x
  * [X] Rush tarde (17-20h): 2.0x
  * [X] Noite/madrugada (22-6h): 0.8x
* [X] Zonas centrais com maior congestionamento (+20%)
* [X] Zonas comerciais com pico ao fim do dia
* [X] Sistema de bloqueio de estradas (`blocked: bool`)
* [X] Método `simular_bloqueio()` para acidentes/obras
* [X] Atualização automática a cada minuto de simulação
* [X] Script de teste independente - `testar_transito.py`

### ✅ Condições Dinâmicas - Falhas

* [X] Sistema completo `GestorFalhas` - `gestor_falhas.py`
* [X] Campo `disponivel: bool` em nós
* [X] Falhas aleatórias em estações (probabilidade configurável)
* [X] Recuperação automática (50% chance por turno)
* [X] Histórico de eventos de falha com timestamps
* [X] Forçar falha manualmente (`forcar_falha()`)
* [X] Recuperar estação manualmente (`recuperar_estacao()`)
* [X] Estatísticas agregadas (taxa disponibilidade por tipo)
* [X] Validação de estação disponível antes de recarga
* [X] Script de teste independente - `testar_falhas.py`
* [X] Integração com simulador (verificação a cada 5 minutos)

### ✅ Métricas de Avaliação

* [X] Sistema completo `Metricas` - `metricas.py`
* [X] **Custos:**
  * [X] Custo total de operação (€)
  * [X] Custo por km diferenciado (elétrico vs combustão)
  * [X] Custo de recarga/abastecimento
  * [X] Taxa ambiental para combustão
  * [X] Bónus para elétricos
* [X] **Emissões:**
  * [X] CO₂ total (kg)
  * [X] 0.0 kg para elétricos
  * [X] 0.12 kg/km para combustão
* [X] **Distâncias:**
  * [X] Km totais percorridos
  * [X] Km sem passageiros
  * [X] Percentagem de km em vazio
* [X] **Pedidos:**
  * [X] Pedidos servidos
  * [X] Pedidos rejeitados
  * [X] Taxa de sucesso (%)
* [X] **Tempo:**
  * [X] Tempo médio de resposta (atendimento - pedido)
  * [X] Tempo total de resposta acumulado
* [X] Integração automática a cada movimento (`integracao_metricas`)
* [X] Método `calcular_metricas()` retorna dict completo

### ✅ Interface Gráfica

* [X] Visualização do mapa - `interface_mapa.py`
  * [X] Canvas tkinter com escala automática
  * [X] Representação de nós por tipo com cores distintas
  * [X] Desenho de arestas (linhas cinzas)
  * [X] Visualização de veículos (quadrados coloridos por estado)
  * [X] Visualização de pedidos (diamantes roxos)
  * [X] Rotas planejadas (linhas tracejadas coloridas)
* [X] Interface principal - `interface_taxigreen.py`
  * [X] Sidebar com scroll
  * [X] Header com tempo atual
  * [X] Seleção de algoritmo (radiobuttons)
  * [X] Painel de métricas (4 cards)
  * [X] Lista de pedidos ativos (scrollable)
  * [X] Log de eventos (scrollable)
  * [X] Botões de controle (Iniciar, Pausar)
* [X] **Tooltips informativos** (hover sobre elementos)
  * [X] Veículos: tipo, autonomia %, estado
  * [X] Nós: tipo, nome
  * [X] Sistema de tooltip dinâmico (on_mouse_move)
* [X] **Legenda visual** completa e clara
* [X] **Atualização em tempo real** (1000ms refresh)
* [X] **Cores semânticas** por estado/tipo

### ✅ Gestão de Autonomia e Recargas

* [X] Verificação proativa de necessidade de recarga (threshold 30%)
* [X] Planeamento de rota para estação mais próxima
* [X] Recarga parcial implementada (`recarga_parcial` float 0.0-1.0)
* [X] Tempo de recarga/abastecimento:
  * [X] Elétrico: 30 min base × parcial
  * [X] Combustão: 10 min base × parcial
* [X] Custo diferenciado por tipo:
  * [X] Elétrico: kWh × €0.15/kWh
  * [X] Combustão: litros × €1.60/litro
* [X] Campo `tempo_ocupado_ate` bloqueia veículo durante recarga
* [X] Estados específicos: `A_CARREGAR`, `A_ABASTECER`
* [X] Transição automática para DISPONIVEL após recarga

### ✅ Sistema de Custos Operacionais

* [X] **Veículos Elétricos:**
  * [X] Custo base: €0.10/km
  * [X] Desgaste reduzido: €0.01/km
  * [X] Bónus ambiental: -€0.02/km
* [X] **Veículos Combustão:**
  * [X] Custo base: €0.20/km
  * [X] Desgaste maior: €0.03/km
  * [X] Taxa ambiental: emissao_CO2 × €0.50/kg
* [X] Método `custo_operacao()` implementado por tipo

### ✅ Preferências Ambientais

* [X] Campo `pref_ambiental` em Pedido
* [X] Validação: "eletrico" | "combustao" | "qualquer"
* [X] Priorização de veículos preferidos em `selecionar_veiculo_pedido()`
* [X] Fallback inteligente se não houver veículos do tipo preferido

### ✅ Sistema de Priorização de Pedidos

* [X] Campo `prioridade: int` em Pedido
* [X] Ordenação na heap: (instante, -prioridade, id)
* [X] Negativo para inverter ordem (maior prioridade primeiro)
* [X] Processamento de pendentes ordenado por prioridade

### ✅ Tempo Máximo de Espera

* [X] Campo `tempo_max_espera: Optional[int]` em Pedido
* [X] Método `expirou(tempo_atual)` implementado
* [X] Verificação em `atribuir_pedidos_pendentes()`
* [X] Estado `CANCELADO` para pedidos expirados
* [X] Contabilização em `pedidos_rejeitados`

### ✅ Gestão de Rotas e Movimento

* [X] Campo `rota: List[str]` em Veiculo
* [X] Campo `indice_rota: int` para progresso
* [X] Método `definir_rota()` inicializa navegação
* [X] Método `mover_um_passo()` com gestão de estados
* [X] Validação de autonomia a cada movimento
* [X] Atualização de `posicao` do veículo
* [X] Registo de km totais e km sem passageiros
* [X] Distinção entre movimento com/sem passageiros

### ✅ Fábrica de Dados Demo

* [X] **Grafo Demo** - `grafo_demo.py`
  * [X] 30 nós (18 recolha, 7 recarga, 5 abastecimento)
  * [X] Layout urbano realista (centro + 4 periferias)
  * [X] 70+ conexões bidirecionais
  * [X] Velocidades variáveis (20-50 km/h)
  * [X] Tempos calculados automaticamente
* [X] **Veículos Demo** - `veiculos_demo.py`
  * [X] 2 elétricos (E1, E2)
  * [X] 2 combustão (C1, C2)
  * [X] Posições iniciais distintas
* [X] **Pedidos Demo** - `pedidos_demo.py`
  * [X] 5 pedidos pré-configurados
  * [X] Instantes diferentes (1, 2, 3, 5, 7 min)
  * [X] Preferências variadas

### ✅ Scripts de Teste

* [X] `testar_algoritmos.py` - Compara 4 algoritmos em 4 cenários
* [X] `testar_transito.py` - Testa variação por hora e bloqueios
* [X] `testar_falhas.py` - Testa falhas aleatórias e forçadas

### ✅ Validações e Tratamento de Erros

* [X] Validação de nós ao adicionar veículos
* [X] Validação de nós ao adicionar pedidos
* [X] Validação de autonomia > 0
* [X] Validação de passageiros > 0
* [X] Validação origem ≠ destino
* [X] Try-catch em cálculo de rotas
* [X] Retorno de rota vazia se impossível
* [X] Validação de estações disponíveis
* [X] Logs de erro informativos

---

## 🔴 **CRÍTICO - Requisitos Fundamentais em Falta**

### 1. **Formulação Formal do Problema de Procura** ⚠️ OBRIGATÓRIO

**Status:** Não documentado (código está implementado mas falta formalização)

Para o relatório, documentar:

#### a) **Estado Inicial (S₀)**

```
S₀ = {
    Veículos: {
        E1: (posicao=Centro, autonomia=80km, capacidade=4, estado=DISPONIVEL),
        E2: (posicao=Praça, autonomia=80km, capacidade=4, estado=DISPONIVEL),
        C1: (posicao=Shopping, autonomia=120km, capacidade=4, estado=DISPONIVEL),
        C2: (posicao=Aeroporto, autonomia=120km, capacidade=4, estado=DISPONIVEL)
    },
    Pedidos: {fila_prioridade ordenada por (instante, prioridade)},
    Grafo: {nós, arestas, congestionamento_inicial, estações_disponíveis},
    Tempo: 0
}
```

#### b) **Teste Objetivo (Goal Test)**

```
Goal(S) = todos_pedidos_atendidos(S) ∧ tempo(S) ≤ duracao_maxima
```

OU com função multi-objetivo:

```
Goal(S) = minimizar f(S) onde:
f(S) = α·custo_total(S) + β·tempo_resposta_medio(S) + 
       γ·emissoes(S) + δ·pedidos_rejeitados(S)
```

#### c) **Operadores (Ações Disponíveis)**

```
1. MOVER(veiculo, origem, destino)
   Pré-condições: veiculo.estado = DISPONIVEL ∧ 
                  veiculo.autonomia ≥ distancia(origem, destino) ∧
                  existe_caminho(origem, destino)
   Efeitos: veiculo.posicao := destino
            veiculo.autonomia -= distancia(origem, destino)
            veiculo.km_total += distancia(origem, destino)
   Custo: tempo_viagem(origem, destino) + custo_operacional(veiculo, distancia)

2. ATRIBUIR(veiculo, pedido)
   Pré-condições: veiculo.estado = DISPONIVEL ∧
                  veiculo.capacidade ≥ pedido.passageiros ∧
                  veiculo.consegue_percorrer(rota_total)
   Efeitos: pedido.estado := ATRIBUIDO
            pedido.veiculo := veiculo.id
            veiculo.rota := calcular_rota(veiculo.pos, pedido.origem, pedido.destino)
   Custo: tempo_total_rota + penalizacao_tempo_espera

3. RECARREGAR(veiculo, estacao, percentagem)
   Pré-condições: estacao.tipo = ESTACAO_RECARGA ∧
                  veiculo.tipo = ELETRICO ∧
                  estacao.disponivel = True
   Efeitos: veiculo.autonomia := min(autonomiaMax, autonomia + capacidade × percentagem)
            veiculo.tempo_ocupado_ate := tempo_atual + tempo_recarga × percentagem
   Custo: kWh_necessarios × custo_kWh + tempo_recarga

4. ABASTECER(veiculo, posto, percentagem)
   Pré-condições: posto.tipo = POSTO_ABASTECIMENTO ∧
                  veiculo.tipo = COMBUSTAO ∧
                  posto.disponivel = True
   Efeitos: veiculo.autonomia := min(autonomiaMax, autonomia + capacidade × percentagem)
            veiculo.tempo_ocupado_ate := tempo_atual + tempo_abastecimento × percentagem
   Custo: litros × custo_litro + tempo_abastecimento + emissoes_CO2
```

#### d) **Função de Custo - IMPLEMENTAR VERSÃO COMPOSTA**

**Atualmente:** Usa apenas tempo de viagem
**Necessário:** Função multi-objetivo ponderada

```python
def custo_composto(estado, acao):
    # Pesos (ajustar experimentalmente)
    α_tempo = 0.4      # Peso do tempo de resposta
    β_custo = 0.3      # Peso do custo operacional
    γ_emissao = 0.2    # Peso das emissões
    δ_rejeicao = 0.1   # Peso de pedidos não atendidos
  
    tempo_total = calcular_tempo_total(estado, acao)
    custo_operacional = calcular_custo_operacional(estado, acao)
    emissoes = calcular_emissoes(estado, acao)
    penalizacao_rejeicao = num_pedidos_rejeitados × 100
  
    return (α_tempo × tempo_total + 
            β_custo × custo_operacional + 
            γ_emissao × emissoes + 
            δ_rejeicao × penalizacao_rejeicao)
```

**TODO:**

* [ ] Documentar formalmente no relatório (Secção 2)
* [ ] Implementar `custo_composto()` em `gestor_frota.py`
* [ ] Adicionar opção para alternar entre custo simples vs composto
* [ ] Justificar escolha de pesos (α, β, γ, δ)

---

### 2.  **Heurística Admissível Avançada para A** * ⚠️ OBRIGATÓRIO

**Status Atual:** Usa apenas distância euclidiana (`dist_euclidiana`)

**Problemas:**

* Não considera autonomia do veículo
* Não estima necessidade de recarga
* Não considera trânsito esperado

**Heurística Melhorada Necessária:**

```python
def heuristica_avancada(grafo, veiculo, no_atual, no_destino, tempo_atual):
    """
    Heurística admissível que considera múltiplos fatores
    """
    # 1. Distância euclidiana base (sempre admissível)
    dist_euclidiana = calcular_distancia_euclidiana(no_atual, no_destino)
  
    # 2. Tempo estimado (velocidade máxima possível = otimista = admissível)
    velocidade_maxima = 50  # km/h (velocidade de autoestrada)
    tempo_base = (dist_euclidiana / velocidade_maxima) * 60  # minutos
  
    # 3. Penalização por autonomia insuficiente (se aplicável)
    penalizacao_autonomia = 0
    if veiculo.autonomia_km < dist_euclidiana:
        # Vai precisar de recarga - estima tempo mínimo de recarga
        autonomia_faltante = dist_euclidiana - veiculo.autonomia_km
        if veiculo.tipo_veiculo() == "eletrico":
            # Tempo mínimo de recarga (otimista)
            penalizacao_autonomia = 15  # 15 min mínimo
        else:
            penalizacao_autonomia = 5   # 5 min mínimo (abastecimento)
  
    # 4. Factor de trânsito esperado (média histórica - otimista)
    hora_atual = (tempo_atual // 60) % 24
    if 7 <= hora_atual <= 9 or 17 <= hora_atual <= 19:
        factor_transito = 1.2  # Rush hour (otimista, pior caso seria 2.0)
    else:
        factor_transito = 1.0
  
    return tempo_base * factor_transito + penalizacao_autonomia
```

**Prova de Admissibilidade:**

* Usa velocidade MÁXIMA possível (nunca sobrestima tempo real)
* Usa factor de trânsito MÍNIMO esperado (nunca sobrestima)
* Penalização de recarga usa tempo MÍNIMO (nunca sobrestima)
* Portanto: h(n) ≤ h*(n) sempre → heurística admissível ✓

**TODO:**

* [ ] Implementar `heuristica_avancada()` em `uteis.py`
* [ ] Modificar `a_star_search()` para usar nova heurística
* [ ] Adicionar parâmetro opcional para escolher heurística (simples vs avançada)
* [ ] Comparar A* simples vs A* avançado no relatório
* [ ] Provar admissibilidade formalmente no relatório

---

### 3. **Otimização de Km Sem Passageiros** ⚠️ IMPORTANTE

**Status:** Campo `km_sem_passageiros` é registado mas não é minimizado ativamente

**Problema:** Veículo pode percorrer 20km para buscar cliente a 25km de distância (desperdício)

**Soluções a Implementar:**

#### a) **Agrupamento Geográfico de Pedidos**

```python
def agrupar_pedidos_proximos(pedidos_pendentes, raio_km=5.0):
    """
    Agrupa pedidos que estão geograficamente próximos
    """
    clusters = []
    visitados = set()
  
    for p1 in pedidos_pendentes:
        if p1.id_pedido in visitados:
            continue
        
        cluster = [p1]
        visitados.add(p1.id_pedido)
    
        for p2 in pedidos_pendentes:
            if p2.id_pedido in visitados:
                continue
            
            # Verifica proximidade de origem E destino
            dist_origem = distancia(p1.posicao_inicial, p2.posicao_inicial)
            dist_destino = distancia(p1.posicao_destino, p2.posicao_destino)
        
            if dist_origem <= raio_km and dist_destino <= raio_km:
                cluster.append(p2)
                visitados.add(p2.id_pedido)
    
        clusters.append(cluster)
  
    return clusters
```

#### b) **Seleção de Veículo por Proximidade Real**

**Atualmente:** Usa rota calculada ✓ (já corrigido)
**Melhorar:** Considerar destino anterior do veículo

```python
def selecionar_veiculo_otimizado(pedido, veiculos_disponiveis):
    """
    Seleciona veículo minimizando dead mileage
    """
    melhor_veiculo = None
    menor_custo_total = float('inf')
  
    for veiculo in veiculos_disponiveis:
        # Distância até pickup
        dist_pickup = calcular_distancia_rota(veiculo.posicao, pedido.origem)
    
        # Distância da viagem com passageiro
        dist_viagem = calcular_distancia_rota(pedido.origem, pedido.destino)
    
        # Custo ponderado: penaliza dead mileage mais que viagem útil
        custo_dead = dist_pickup * 2.0  # Penalização 2x
        custo_util = dist_viagem * 1.0
        custo_total = custo_dead + custo_util
    
        if custo_total < menor_custo_total:
            menor_custo_total = custo_total
            melhor_veiculo = veiculo
  
    return melhor_veiculo
```

#### c) **Reposicionamento Proativo** (Bónus)

```python
def reposicionar_veiculo_ocioso(veiculo, pedidos_futuros):
    """
    Move veículo para zona de alta demanda esperada
    """
    # Analisa pedidos futuros (próximos 10 minutos)
    zonas_demanda = {}
    for p in pedidos_futuros:
        if p.instante_pedido <= tempo_atual + 10:
            zona = p.posicao_inicial
            zonas_demanda[zona] = zonas_demanda.get(zona, 0) + 1
  
    # Move para zona de maior demanda
    if zonas_demanda:
        zona_alvo = max(zonas_demanda, key=zonas_demanda.get)
        veiculo.definir_rota(calcular_rota(veiculo.posicao, zona_alvo))
```

**TODO:**

* [ ] Implementar `agrupar_pedidos_proximos()` em `gestor_frota.py`
* [ ] Modificar `selecionar_veiculo_pedido()` para usar penalização de dead mileage
* [ ] (Opcional) Implementar `reposicionar_veiculo_ocioso()`
* [ ] Comparar km sem passageiros antes/depois no relatório

---

### 4. **Experimentação Sistemática** ⚠️ OBRIGATÓRIO

**Status:** Scripts de teste existem mas não há experimentação rigorosa

**Necessário para o Relatório:**

#### Criar 5+ Cenários de Teste Padronizados

```python
# Ficheiro: experimentos.py

CENARIOS = {
    "baixa_demanda": {
        "num_pedidos": 5,
        "duracao": 60,
        "usar_transito": False,
        "usar_falhas": False,
        "descricao": "5 pedidos em 60 min, sem perturbações"
    },
  
    "alta_demanda": {
        "num_pedidos": 20,
        "duracao": 60,
        "usar_transito": False,
        "usar_falhas": False,
        "descricao": "20 pedidos em 60 min (stress test)"
    },
  
    "rush_hour": {
        "num_pedidos": 15,
        "duracao": 60,
        "usar_transito": True,
        "inicio_hora": 8,  # 8h da manhã
        "descricao": "15 pedidos durante rush hour"
    },
  
    "falhas_estacoes": {
        "num_pedidos": 10,
        "duracao": 60,
        "usar_transito": False,
        "usar_falhas": True,
        "prob_falha": 0.15,
        "descricao": "10 pedidos com 15% falhas em estações"
    },
  
    "frota_eletrica": {
        "num_pedidos": 15,
        "duracao": 60,
        "frota": "100% elétrica",
        "descricao": "Teste com apenas veículos elétricos"
    },
  
    "frota_combustao": {
        "num_pedidos": 15,
        "duracao": 60,
        "frota": "100% combustão",
        "descricao": "Teste com apenas veículos a combustão"
    }
}

def executar_experimento(cenario_nome, algoritmo):
    """Executa um cenário de teste com um algoritmo específico"""
    # ... código de execução
    return resultados

def comparar_todos_algoritmos():
    """Compara todos os algoritmos em todos os cenários"""
    algoritmos = ["astar", "ucs", "bfs", "dfs"]
  
    resultados_completos = {}
  
    for cenario_nome in CENARIOS:
        resultados_completos[cenario_nome] = {}
    
        for algoritmo in algoritmos:
            print(f"\nExecutando: {cenario_nome} com {algoritmo.upper()}")
            resultado = executar_experimento(cenario_nome, algoritmo)
            resultados_completos[cenario_nome][algoritmo] = resultado
  
    return resultados_completos

def gerar_tabelas_latex(resultados):
    """Gera tabelas em LaTeX para o relatório"""
    # ... código de formatação
  
def gerar_graficos_comparativos(resultados):
    """Gera gráficos matplotlib"""
    # ... código de visualização
```

**TODO:**

* [ ] Criar `experimentos.py` com 6 cenários padronizados
* [ ] Implementar exec

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
