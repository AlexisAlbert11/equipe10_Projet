import route_solution as rsol
import busfleet_bus as bfleet
import élève_solution as élève

class Final:
    def __init__(self, result, problem, bus_fleet: bfleet.BusFleet, eleves: élève.Eleves, lieux):
        self.route = result["route"]
        self.assignation = result["assignation"]
        self.nb_etudiant_dans_bus = result["nb_etudiant_dans_bus"]
        self.temps = result["temps"]
        self.problem = problem
        self.bus_fleet = bus_fleet
        self.eleves = eleves
        self.lieux = lieux

    def afficher(self):
        """Affiche tous les résultats de manière claire dans le terminal."""
        print("=== Résultats de la résolution ===")
        print(f"Séquence valide : {self.route.validate()}")
        print(f"Distance totale parcourue : {self.route.evaluate():.2f} km")
        print(f"Assignations valides : {self.bus_fleet.evaluate()}")
        print(f"Nombre d'étudiants ramassés : {self.eleves.validate(self.nb_etudiant_dans_bus)}")  # Ajouté
        print(f"Tous les étudiants ramassés : {self.eleves.evaluate(self.nb_etudiant_dans_bus)}")
        print(f"Nombre de bus disponibles : {self.bus_fleet.count_available_buses()}")
        print(f"Nombre de bus utilisés : {self.bus_fleet.count_used_buses()}")

        print("\nHeures de départ des bus :")
        departure_times = self.bus_fleet.departure_times(self.temps)
        for bus_idx, time in departure_times.items():
            print(f"  Bus {bus_idx} : {time}")

        print("\nItinéraires des bus :")
        for bus_idx, seq in self.route.visit_sequences.items():
            if seq:
                route_str = " -> ".join(self.lieux[i] for i in seq)
                print(f"  Bus {bus_idx} : {route_str}")

        print("==================================")