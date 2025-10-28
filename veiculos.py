"""
Modelo de veículo (elétrico ou a combustão).
Contém propriedades de autonomia, consumo e custo por km.
"""

from dataclasses import dataclass

@dataclass
class Vehicle:
    id: str
    position: str             # localizacao atual
    is_electric: bool
    autonomy_km: float        # autonomia atual (km restantes)
    autonomy_max_km: float    # autonomia máxima
    passenger_capacity: int
    cost_per_km: float        # custo operacional (energia ou combustível)
    available: bool = True    # disponibilidade do veículo

    """Verifica se o veículo pode percorrer determinada distância."""
    def can_reach(self, distance_km: float) -> bool:
        return self.autonomy_km >= distance_km

    """Atualiza autonomia e posição após percorrer certa distância."""
    def move(self, distance_km: float):
        self.autonomy_km = max(0.0, self.autonomy_km - distance_km)
        #todo: falta atualizar a posição
    
    """Recarrega bateria ou reabastece tanque."""
    def recharge_or_refuel(self):
        self.autonomy_km = self.autonomy_max_km

    """Cálculo do custo de operação."""
    def operating_cost(self, distance_km: float) -> float:
        return self.cost_per_km * distance_km
