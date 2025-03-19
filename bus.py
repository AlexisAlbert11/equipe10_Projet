import solution as sol
import copy

# Sert à structurer les données et vérifier si les lieux ont un seul bus à part école et entrepriseclass Bus:
class Bus:
    def __init__(self, id, capacity, cost_per_km, startup_cost):
        self.id = copy.deepcopy(id)
        self.capacity = copy.deepcopy(capacity)
        self.cost_per_km = copy.deepcopy(cost_per_km)
        self.startup_cost = copy.deepcopy(startup_cost)

    def __str__(self):
        return (f"Bus {self.id} - Capacity: {self.capacity}, "
                f"Cost/km: {self.cost_per_km}, Startup Cost: {self.startup_cost}")

    