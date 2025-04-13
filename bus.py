import solution as sol
import copy

# Sert à structurer les données et vérifier si les lieux ont un seul bus à part école et entrepriseclass Bus:
class Bus:
    def __init__(self, id, capacity, cost_per_km, startup_cost):
        super().__init__()  # Appel au constructeur parent, None si pas de problem requis
        self.id = copy.deepcopy(id)
        self.capacity = copy.deepcopy(capacity)
        self.cost_per_km = copy.deepcopy(cost_per_km)
        self.startup_cost = copy.deepcopy(startup_cost)
        Bus.nombre_de_bus += 1  # Incrémente le compteur à chaque création
        #self.bus = [self.id, self.capacity, self.cost_per_km, self.startup_cost]
        

    def evaluate(self):
        pass  # À implémenter si nécessaire

    def validate(self):
        pass  # À implémenter si nécessaire

    def heure_depart(self):
        pass  # À implémenter si nécessaire

    def __str__(self):
        return (f"Bus {self.id} - Capacity: {self.capacity}, "
                f"Cost/km: {self.cost_per_km}, Startup Cost: {self.startup_cost}")

    