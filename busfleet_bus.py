import bus as bus  # Importe le module bus pour accéder à la classe Bus
from datetime import datetime, timedelta

class BusFleet:
    def __init__(self, buses, avg_speed):
        self.buses = buses  # Liste des 15 bus de buses1
        self.avg_speed = avg_speed  # vitesse_moyenne
        self.assignation = None  # Initialisé à None, sera rempli après résolution

    def set_assignation(self, assignments):
        """Méthode pour définir les assignations après résolution."""
        self.assignation = assignments

    def evaluate(self):
        """
        Vérifie si chaque lieu (sauf 0 et 1) est assigné à un seul bus.
        Utilise self.assignation.
        """
        if self.assignation is None:
            raise ValueError("Assignation non définie.")
        assigned_locations = {}
        for (loc, bus_idx), value in self.assignation.items():
            if value == 1 and loc not in [0, 1]:  # Sauf entreprise (0) et école (1)
                if loc in assigned_locations:
                    return False  # Lieu assigné à plusieurs bus
                assigned_locations[loc] = bus_idx
        return True

    def departure_times(self, times):
        school_time = datetime.strptime("08:00", "%H:%M")
        departure_times = {}
        for b in range(len(self.buses)):
            total_time = 0
            for (i, j, bus_idx), t in times.items():
                if bus_idx == b and j == 1 and t > 0:
                    total_time += t
            if total_time > 0:
                departure = school_time - timedelta(minutes=total_time)
                departure_times[b] = departure.strftime("%H:%M")
            else:
                departure_times[b] = "Pas utilisé"
        return departure_times

    def count_available_buses(self):
        return len(self.buses)

    def count_used_buses(self):
        if self.assignation is None:
            raise ValueError("Assignation non définie.")
        used_buses = set()
        for (loc, bus_idx), value in self.assignation.items():
            if value == 1:
                used_buses.add(bus_idx)
        return len(used_buses)

    def __str__(self):
        return f"Bus fleet avec {len(self.buses)} autobus, vitesse moyenne: {self.avg_speed} km/h"