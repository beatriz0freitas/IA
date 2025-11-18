"""
Algoritmo de Ride-Sharing SIMPLIFICADO - Sem problemas de hashable
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from modelo.pedidos import Pedido, EstadoPedido
from modelo.veiculos import Veiculo, EstadoVeiculo


@dataclass
class GrupoPassageiros:
    """Grupo de pedidos que viajam juntos"""
    pedidos: List[Pedido] = field(default_factory=list)
    veiculo: Optional[Veiculo] = None
    rota_completa: List[str] = field(default_factory=list)
    passageiros_totais: int = 0


class RideSharing:
    """Gerencia agrupamento simples de pedidos"""
    
    def __init__(self, gestor_frota):
        self.gestor = gestor_frota
        self.grupos_ativos: Dict[str, GrupoPassageiros] = {}
        self.historico_ocupacao = []
    
    def agrupar_pedidos(self) -> List[GrupoPassageiros]:
        """
        Agrupa pedidos PENDENTES de forma simples.
        Agrupa pedidos com mesma origem/destino próximos.
        """
        pedidos_pendentes = [
            p for p in self.gestor.pedidos_pendentes
            if p.estado == EstadoPedido.PENDENTE
        ]
        
        if not pedidos_pendentes:
            return []
        
        # Ordenar por prioridade
        pedidos_pendentes.sort(key=lambda p: -p.prioridade)
        
        grupos = []
        processados = []  # Lista de IDs processados
        
        for i, pedido in enumerate(pedidos_pendentes):
            if pedido.id_pedido in processados:
                continue
            
            # Criar novo grupo
            novo_grupo = GrupoPassageiros(pedidos=[pedido])
            novo_grupo.passageiros_totais = pedido.passageiros
            processados.append(pedido.id_pedido)
            
            # Tentar agregar outros pedidos similares
            for outro in pedidos_pendentes[i+1:]:
                if outro.id_pedido in processados:
                    continue
                
                # Critérios: capacidade, preferência ambiental
                novo_total = novo_grupo.passageiros_totais + outro.passageiros
                if novo_total > 4:  # Capacidade máxima
                    continue
                
                # Preferência ambiental compatível
                if (pedido.pref_ambiental != "qualquer" and 
                    outro.pref_ambiental != "qualquer"):
                    if pedido.pref_ambiental != outro.pref_ambiental:
                        continue
                
                # Adicionar ao grupo
                novo_grupo.pedidos.append(outro)
                novo_grupo.passageiros_totais = novo_total
                processados.append(outro.id_pedido)
            
            grupos.append(novo_grupo)
        
        return grupos
    
    def atribuir_grupos_otimizado(self) -> List[GrupoPassageiros]:
        """Atribui grupos a veículos"""
        grupos = self.agrupar_pedidos()
        
        if not grupos:
            return []
        
        atribuicoes = []
        
        for grupo in grupos:
            # Selecionar veículo
            veiculo = self._selecionar_veiculo_grupo(grupo)
            
            if not veiculo:
                # Rejeitar pedidos do grupo
                for p in grupo.pedidos:
                    p.estado = EstadoPedido.REJEITADO
                continue
            
            grupo.veiculo = veiculo
            
            # Calcular rota simples
            rota = self._calcular_rota_grupo(grupo, veiculo)
            
            if not rota:
                for p in grupo.pedidos:
                    p.estado = EstadoPedido.REJEITADO
                continue
            
            # Marcar todos os pedidos como atribuídos
            for pedido in grupo.pedidos:
                pedido.veiculo_atribuido = veiculo.id_veiculo
                pedido.estado = EstadoPedido.ATRIBUIDO
            
            grupo.rota_completa = rota
            self.grupos_ativos[veiculo.id_veiculo] = grupo
            atribuicoes.append(grupo)
            
            # Definir rota no veículo
            veiculo.definir_rota(rota)
            veiculo.estado = EstadoVeiculo.EM_DESLOCACAO
        
        return atribuicoes
    
    def _selecionar_veiculo_grupo(self, grupo: GrupoPassageiros) -> Optional[Veiculo]:
        """Seleciona veículo para o grupo"""
        candidatos = []
        
        for v in self.gestor.veiculos_disponiveis():
            # Capacidade
            if v.capacidade_passageiros < grupo.passageiros_totais:
                continue
            
            # Preferência ambiental
            pref = grupo.pedidos[0].pref_ambiental
            if pref != "qualquer" and v.tipo_veiculo() != pref:
                continue
            
            candidatos.append(v)
        
        if not candidatos:
            return None
        
        # Retornar o mais próximo
        try:
            origem = grupo.pedidos[0].posicao_inicial
            return min(
                candidatos,
                key=lambda v: self.gestor.grafo.distancia(v.posicao, origem)
            )
        except:
            return candidatos[0] if candidatos else None
    
    def _calcular_rota_grupo(self, grupo: GrupoPassageiros, veiculo: Veiculo) -> List[str]:
        """Calcula rota que visita todas as origens e destinos"""
        rota = [veiculo.posicao]
        
        # Adicionar origens
        for pedido in grupo.pedidos:
            try:
                caminho, _ = self.gestor.calcular_rota(rota[-1], pedido.posicao_inicial)
                if caminho:
                    rota.extend(caminho[1:])
            except:
                pass
        
        # Adicionar destinos
        for pedido in grupo.pedidos:
            try:
                caminho, _ = self.gestor.calcular_rota(rota[-1], pedido.posicao_destino)
                if caminho:
                    rota.extend(caminho[1:])
            except:
                pass
        
        # Remover duplicados consecutivos
        rota_limpa = []
        for no in rota:
            if not rota_limpa or no != rota_limpa[-1]:
                rota_limpa.append(no)
        
        return rota_limpa if len(rota_limpa) > 1 else []
    
    def registar_ocupacao(self) -> float:
        """Calcula ocupação média"""
        ocupacoes = []
        for v in self.gestor.veiculos.values():
            if v.estado in (EstadoVeiculo.A_SERVICO, EstadoVeiculo.EM_DESLOCACAO):
                pedidos_v = [
                    p for p in self.gestor.pedidos_pendentes
                    if p.veiculo_atribuido == v.id_veiculo
                ]
                if pedidos_v:
                    ocupacao = sum(p.passageiros for p in pedidos_v) / v.capacidade_passageiros
                    ocupacoes.append(ocupacao)
        
        if ocupacoes:
            media = sum(ocupacoes) / len(ocupacoes)
            self.historico_ocupacao.append(media)
            return media
        return 0.0
    
    def gerar_relatorio(self) -> Dict:
        """Gera relatório de eficiência"""
        return {
            "ocupacao_media": (
                sum(self.historico_ocupacao) / len(self.historico_ocupacao)
                if self.historico_ocupacao else 0.0
            ),
            "grupos_ativos": len(self.grupos_ativos),
            "total_passageiros_agrupados": sum(
                g.passageiros_totais for g in self.grupos_ativos.values()
            ),
            "eficiencia": "Alta ocupação" if (
                sum(self.historico_ocupacao) / len(self.historico_ocupacao) > 0.7
                if self.historico_ocupacao else False
            ) else "Ocupação baixa"
        }