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
