"""
Sistema de comparação de algoritmos de procura.
Testa e compara A*, UCS, BFS, DFS em diferentes cenários.

- Comparar estratégias de procura (informada vs não informada)
- Avaliar eficiência com métricas quantitativas
- Considerar condições variáveis (trânsito, autonomia)
"""

from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass, field
import time
import statistics
from modelo.grafo import Grafo
from modelo.veiculos import Veiculo

#todo: limpar aspetos menos necessários

@dataclass
class ResultadoAlgoritmo:
    """Resultado detalhado da execução de um algoritmo."""
    nome_algoritmo: str
    tempo_execucao_ms: float
    nos_expandidos: int
    custo_solucao: float
    tamanho_caminho: int
    caminho: List[str]
    sucesso: bool
    memoria_pico_kb: float = 0.0  # Uso de memória estimado
    
    def eficiencia_relativa(self, referencia: 'ResultadoAlgoritmo') -> float:
        """
        Calcula eficiência relativa comparado com algoritmo de referência.
        
        Returns:
            Valor > 1.0 = mais eficiente que referência
            Valor < 1.0 = menos eficiente
        """
        if not self.sucesso or not referencia.sucesso:
            return 0.0
        
        # Score ponderado: 40% tempo, 30% nós, 30% qualidade
        score_tempo = referencia.tempo_execucao_ms / max(self.tempo_execucao_ms, 0.001)
        score_nos = referencia.nos_expandidos / max(self.nos_expandidos, 1)
        score_custo = referencia.custo_solucao / max(self.custo_solucao, 0.001)
        
        return 0.4 * score_tempo + 0.3 * score_nos + 0.3 * score_custo


@dataclass
class CenarioTeste:
    """Cenário de teste para algoritmos."""
    nome: str
    origem: str
    destino: str
    descricao: str
    veiculo: Veiculo = None  # Para testar heurísticas avançadas
    tempo_simulacao: int = 0  # Para testar com trânsito


class ComparadorAlgoritmos:
    """Compara diferentes algoritmos de procura no mesmo cenário"""
    grafo: Grafo
    resultados: List[ResultadoAlgoritmo] = field(default_factory=list)

    def testar_algoritmo(self, nome: str, funcao_busca: Callable,
                    origem: str, destino: str) -> ResultadoAlgoritmo:
        """
        Executa um algoritmo e regista métricas.
        """

        # Instrumentação genérica: conta nós expandidos como “nós para os quais vizinhos(nó)
        # foi chamado”. Funciona para A*, UCS, BFS, DFS, etc., desde que usem grafo.vizinhos().
        orig_vizinhos = getattr(self.grafo, "vizinhos", None)
        expandidos_unicos: set[str] = set()

        def vizinhos_contador(no_id: str):
            expandidos_unicos.add(no_id)
            return orig_vizinhos(no_id)

        inicio = time.perf_counter()
        nos_expandidos = 0
        
        try:
            if orig_vizinhos is not None:
                self.grafo.vizinhos = vizinhos_contador  # type: ignore[attr-defined]

            # Executa algoritmo
            if cenario.veiculo and "astar" in nome.lower():
                # A* com contexto (veículo + tempo)
                resultado = funcao_busca(
                    self.grafo, cenario.origem, cenario.destino,
                    veiculo=cenario.veiculo,
                    tempo_atual=cenario.tempo_simulacao
                )
            else:
                resultado = funcao_busca(
                    self.grafo, cenario.origem, cenario.destino
                )
            
            # Interpreta resultado
            if isinstance(resultado, tuple):
                custo = resultado[0]
                caminho = resultado[1]
            else:
                caminho = resultado
                custo = self.calcular_custo_caminho(caminho) if caminho else float('inf')
            
            fim = time.perf_counter()
            tempo_ms = (fim - inicio) * 1000
            
            # Estima nós expandidos (aproximação pelo tamanho do caminho)
            nos_expandidos = len(expandidos_unicos) if orig_vizinhos is not None else 0
            
            # Estima uso de memória (estruturas de dados típicas)
            memoria_kb = self.estimar_memoria(caminho, nos_expandidos)
            
            sucesso = bool(caminho) and custo != float('inf')
            
            return ResultadoAlgoritmo(
                nome_algoritmo=nome,
                tempo_execucao_ms=round(tempo_ms, 3),
                nos_expandidos=nos_expandidos,
                custo_solucao=round(custo, 2),
                tamanho_caminho=len(caminho) if caminho else 0,
                caminho=caminho if caminho else [],
                sucesso=sucesso,
                memoria_pico_kb=memoria_kb
            )
        
        except Exception as e:
            fim = time.perf_counter()
            tempo_ms = (fim - inicio) * 1000
            
            print(f"Erro em {nome}: {e}")
            
            return ResultadoAlgoritmo(
                nome_algoritmo=nome,
                tempo_execucao_ms=round(tempo_ms, 3),
                nos_expandidos=0,
                custo_solucao=float('inf'),
                tamanho_caminho=0,
                caminho=[],
                sucesso=False
            )
    
    def calcular_custo_caminho(self, caminho: List[str]) -> float:
        """Calcula custo total de um caminho."""
        if not caminho or len(caminho) < 2:
            return 0.0
        
        custo = 0.0
        for i in range(len(caminho) - 1):
            try:
                aresta = self.grafo.get_aresta(caminho[i], caminho[i + 1])
                custo += aresta.tempo_real()
            except ValueError:
                return float('inf')
        
        return custo
    
    def estimar_memoria(self, caminho: List[str], nos_expandidos: int) -> float:
        """
        Estima uso de memória do algoritmo.
        
        Baseado em:
        - Tamanho das estruturas (open_set, closed_set, etc.)
        - Caminho encontrado
        """
        # Cada nó armazena: ID (string ~20 bytes) + custo (8 bytes) + ponteiro (8 bytes)
        bytes_por_no = 36
        
        # Estruturas típicas dos algoritmos
        memoria_bytes = (nos_expandidos * bytes_por_no) + (len(caminho) * 20)
        
        return round(memoria_bytes / 1024, 2)  # Converte para KB
    
    def comparar_multiplos(self, algoritmos: Dict[str, Callable],
                          cenario: CenarioTeste) -> List[ResultadoAlgoritmo]:
        """
        Compara múltiplos algoritmos no mesmo cenário.
        
        Args:
            algoritmos: Dict com {nome: função_busca}
            cenario: Cenário de teste
            
        Returns:
            Lista de resultados ordenada por eficiência
        """
        self.resultados = []
        
        print(f"\n{'='*80}")
        print(f"CENÁRIO: {cenario.nome}")
        print(f"Origem: {cenario.origem} | Destino: {cenario.destino}")
        print(f"Descrição: {cenario.descricao}")
        print(f"{'='*80}\n")
        
        for nome, funcao in algoritmos.items():
            print(f"Testando {nome}...", end=" ")
            resultado = self.testar_algoritmo(nome, funcao, cenario)
            self.resultados.append(resultado)
            
            # Armazena no histórico
            if nome not in self.historico:
                self.historico[nome] = []
            self.historico[nome].append(resultado)
            
            status = "✓" if resultado.sucesso else "✗"
            print(f"{status} ({resultado.tempo_execucao_ms:.3f} ms)")
        
        # Ordena por eficiência (tempo + qualidade)
        self.resultados.sort(key=lambda r: (
            not r.sucesso,  # Sucessos primeiro
            r.tempo_execucao_ms if r.sucesso else float('inf')
        ))
        
        return self.resultados
    
    def comparar_batch(self, algoritmos: Dict[str, Callable],
                      cenarios: List[CenarioTeste]) -> Dict[str, List[ResultadoAlgoritmo]]:
        """
        Compara algoritmos em múltiplos cenários (batch testing).
        
        Returns:
            Dict com resultados por cenário
        """
        resultados_batch = {}
        
        for cenario in cenarios:
            resultados = self.comparar_multiplos(algoritmos, cenario)
            resultados_batch[cenario.nome] = resultados
        
        return resultados_batch
    
    def gerar_relatorio_texto(self) -> str:
        """Gera relatório em texto dos resultados."""
        if not self.resultados:
            return "Nenhum resultado disponível."
        
        linhas = []
        linhas.append("\n" + "="*90)
        linhas.append("COMPARAÇÃO DE ALGORITMOS DE PROCURA")
        linhas.append("="*90)
        linhas.append("")
        
        # Cabeçalho
        linhas.append(
            f"{'Algoritmo':<15} {'Tempo (ms)':<12} {'Nós':<8} {'Custo':<10} "
            f"{'Caminho':<10} {'Memória (KB)':<12} {'Status':<8}"
        )
        linhas.append("-"*90)
        
        # Resultados
        for r in self.resultados:
            sucesso = "✓" if r.sucesso else "✗"
            custo_str = f"{r.custo_solucao:.1f}" if r.custo_solucao != float('inf') else "INF"
            
            linhas.append(
                f"{r.nome_algoritmo:<15} "
                f"{r.tempo_execucao_ms:<12.3f} "
                f"{r.nos_expandidos:<8} "
                f"{custo_str:<10} "
                f"{r.tamanho_caminho:<10} "
                f"{r.memoria_pico_kb:<12.2f} "
                f"{sucesso:<8}"
            )
        
        linhas.append("="*90)
        
        # Análise comparativa
        linhas.append("\nANÁLISE COMPARATIVA:")
        linhas.append("-"*90)
        
        sucessos = [r for r in self.resultados if r.sucesso]
        if sucessos:
            # Mais rápido
            mais_rapido = min(sucessos, key=lambda r: r.tempo_execucao_ms)
            linhas.append(
                f"  Mais rápido: {mais_rapido.nome_algoritmo} "
                f"({mais_rapido.tempo_execucao_ms:.3f} ms)"
            )
            
            # Melhor solução
            melhor_custo = min(sucessos, key=lambda r: r.custo_solucao)
            linhas.append(
                f"  Melhor solução: {melhor_custo.nome_algoritmo} "
                f"(custo {melhor_custo.custo_solucao:.1f})"
            )
            
            # Menos nós expandidos
            menos_nos = min(sucessos, key=lambda r: r.nos_expandidos)
            linhas.append(
                f"  Menos nós: {menos_nos.nome_algoritmo} "
                f"({menos_nos.nos_expandidos} nós)"
            )
            
            # Menos memória
            menos_memoria = min(sucessos, key=lambda r: r.memoria_pico_kb)
            linhas.append(
                f"  Menos memória: {menos_memoria.nome_algoritmo} "
                f"({menos_memoria.memoria_pico_kb:.2f} KB)"
            )
            
            # Eficiência relativa (comparado com o mais rápido)
            linhas.append("\n  EFICIÊNCIA RELATIVA (vs mais rápido):")
            for r in sucessos:
                if r != mais_rapido:
                    ef = r.eficiencia_relativa(mais_rapido)
                    linhas.append(f"    {r.nome_algoritmo}: {ef:.2f}x")
        else:
            linhas.append("  ⚠️  Nenhum algoritmo encontrou solução!")
        
        linhas.append("")
        return "\n".join(linhas)
    
    def gerar_estatisticas_historico(self) -> str:
        """
        Gera estatísticas agregadas do histórico de testes.
        Útil para avaliar consistência dos algoritmos.
        """
        if not self.historico:
            return "Sem histórico disponível."
        
        linhas = []
        linhas.append("\n" + "="*80)
        linhas.append("ESTATÍSTICAS DO HISTÓRICO DE TESTES")
        linhas.append("="*80)
        linhas.append("")
        
        for nome_algo, resultados in self.historico.items():
            sucessos = [r for r in resultados if r.sucesso]
            
            if not sucessos:
                linhas.append(f"{nome_algo}: Sem sucessos registrados")
                continue
            
            # Estatísticas
            tempos = [r.tempo_execucao_ms for r in sucessos]
            custos = [r.custo_solucao for r in sucessos]
            
            linhas.append(f"{nome_algo}:")
            linhas.append(f"  Testes: {len(resultados)} | Sucessos: {len(sucessos)} ({len(sucessos)/len(resultados)*100:.1f}%)")
            linhas.append(f"  Tempo médio: {statistics.mean(tempos):.3f} ms (±{statistics.stdev(tempos) if len(tempos) > 1 else 0:.3f})")
            linhas.append(f"  Custo médio: {statistics.mean(custos):.2f} (±{statistics.stdev(custos) if len(custos) > 1 else 0:.2f})")
            linhas.append("")
        
        return "\n".join(linhas)
    
    