"""
Sistema de comparação de algoritmos de procura.
Permite testar e comparar o desempenho de diferentes algoritmos (A*, UCS, BFS, DFS).
"""

from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass, field
import time
from modelo.grafo import Grafo


@dataclass
class ResultadoAlgoritmo:
    """Resultado da execução de um algoritmo"""
    nome_algoritmo: str
    tempo_execucao_ms: float
    nos_expandidos: int
    custo_solucao: float
    tamanho_caminho: int
    caminho: List[str]
    sucesso: bool


@dataclass
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

        try:
            if orig_vizinhos is not None:
                self.grafo.vizinhos = vizinhos_contador  # type: ignore[attr-defined]

            # Executa algoritmo
            resultado = funcao_busca(self.grafo, origem, destino)

            # Interpreta resultado (alguns retornam (custo, caminho), outros só caminho)
            if isinstance(resultado, tuple):
                custo = resultado[0]
                caminho = resultado[1]
            else:
                caminho = resultado
                custo = self._calcular_custo_caminho(caminho) if caminho else float('inf')

            fim = time.perf_counter()
            tempo_ms = (fim - inicio) * 1000
            sucesso = bool(caminho) and custo != float('inf')

            nos_expandidos = len(expandidos_unicos) if orig_vizinhos is not None else 0

            return ResultadoAlgoritmo(
                nome_algoritmo=nome,
                tempo_execucao_ms=round(tempo_ms, 3),
                nos_expandidos=nos_expandidos,
                custo_solucao=custo,
                tamanho_caminho=len(caminho) if caminho else 0,
                caminho=caminho if caminho else [],
                sucesso=sucesso
            )

        except Exception:
            fim = time.perf_counter()
            tempo_ms = (fim - inicio) * 1000

            return ResultadoAlgoritmo(
                nome_algoritmo=nome,
                tempo_execucao_ms=round(tempo_ms, 3),
                nos_expandidos=0,
                custo_solucao=float('inf'),
                tamanho_caminho=0,
                caminho=[],
                sucesso=False
            )

        finally:
            # Restaura método original (para não afetar execuções seguintes)
            if orig_vizinhos is not None:
                self.grafo.vizinhos = orig_vizinhos  # type: ignore[attr-defined]



    def _calcular_custo_caminho(self, caminho: List[str]) -> float:
        """Calcula custo total de um caminho"""
        if not caminho or len(caminho) < 2:
            return 0.0

        custo = 0.0
        for i in range(len(caminho) - 1):
            try:
                aresta = self.grafo.get_aresta(caminho[i], caminho[i + 1])
                custo += aresta.tempoViagem_min
            except ValueError:
                return float('inf')

        return custo


    def comparar_multiplos(self, algoritmos: Dict[str, Callable],
                          origem: str, destino: str) -> List[ResultadoAlgoritmo]:
        """
        Compara múltiplos algoritmos no mesmo problema.

        Args:
            algoritmos: Dict com {nome: função_busca}
            origem: Nó de origem
            destino: Nó de destino

        Returns:
            Lista de ResultadoAlgoritmo ordenada por tempo de execução
        """
        self.resultados = []

        for nome, funcao in algoritmos.items():
            resultado = self.testar_algoritmo(nome, funcao, origem, destino)
            self.resultados.append(resultado)

        # Ordena por tempo de execução
        self.resultados.sort(key=lambda r: (not r.sucesso, r.custo_solucao, r.tempo_execucao_ms))

        return self.resultados


    def gerar_relatorio_texto(self) -> str:
        """Gera relatório em texto dos resultados"""
        if not self.resultados:
            return "Nenhum resultado disponível."

        linhas = []
        linhas.append("\n" + "="*80)
        linhas.append("COMPARAÇÃO DE ALGORITMOS DE PROCURA")
        linhas.append("="*80)
        linhas.append("")

        # Cabeçalho da tabela
        linhas.append(f"{'Algoritmo':<12} {'Tempo (ms)':<12} {'Nós Exp.':<12} {'Custo':<12} {'Tamanho':<12} {'Sucesso':<10}")
        linhas.append("-"*80)

        for r in self.resultados:
            sucesso_str = "✓" if r.sucesso else "✗"
            custo_str = f"{r.custo_solucao:.2f}" if r.custo_solucao != float('inf') else "INF"

            linhas.append(
                f"{r.nome_algoritmo:<12} "
                f"{r.tempo_execucao_ms:<12.3f} "
                f"{r.nos_expandidos:<12} "
                f"{custo_str:<12} "
                f"{r.tamanho_caminho:<12} "
                f"{sucesso_str:<10}"
            )

        linhas.append("="*80)

        # Análise
        linhas.append("\nANÁLISE:")

        sucessos = [r for r in self.resultados if r.sucesso]
        if sucessos:
            mais_rapido = min(sucessos, key=lambda r: r.tempo_execucao_ms)
            linhas.append(f"  • Mais rápido: {mais_rapido.nome_algoritmo} ({mais_rapido.tempo_execucao_ms:.3f} ms)")

            melhor_custo = min(sucessos, key=lambda r: r.custo_solucao)
            linhas.append(f"  • Melhor solução: {melhor_custo.nome_algoritmo} (custo {melhor_custo.custo_solucao:.2f})")

            menor_caminho = min(sucessos, key=lambda r: r.tamanho_caminho)
            linhas.append(f"  • Caminho mais curto: {menor_caminho.nome_algoritmo} ({menor_caminho.tamanho_caminho} nós)")
        else:
            linhas.append("  • Nenhum algoritmo encontrou solução!")

        linhas.append("")

        return "\n".join(linhas)


    def gerar_relatorio_dict(self) -> Dict:
        """Gera relatório em formato dicionário (para JSON/export)"""
        return {
            "total_algoritmos": len(self.resultados),
            "algoritmos": [
                {
                    "nome": r.nome_algoritmo,
                    "tempo_ms": r.tempo_execucao_ms,
                    "nos_expandidos": r.nos_expandidos,
                    "custo": r.custo_solucao,
                    "tamanho_caminho": r.tamanho_caminho,
                    "sucesso": r.sucesso
                }
                for r in self.resultados
            ]
        }
