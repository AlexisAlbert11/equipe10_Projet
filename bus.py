import solution as sol
import copy
#Sert a strucutre les données et de vérfier si les lieux ont un seul bus à part école et entreprise
class Bus(sol.Solution):
    def __init__(self, id, capacity, cost_per_km, startup_cost, count = -1):
        self.id = copy.deepcopy(id)
        self.capacity = copy.deepcopy(capacity)
        self.cost_per_km = copy.deepcopy(cost_per_km)
        self.startup_cost = copy.deepcopy(startup_cost)
        self.count_buses = 0

    def count_buses(self):
        return len(self.id)
    
    def evaluate(self):
        pass

    def validate(self):
        pass

    def heure_depart(self):
        pass