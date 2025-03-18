import solution as sol
import bus as bus
import fastroute_problem as frp


class Route(sol.Solution):
    def __init__(self, problem):
        super().__init__(problem)
        self.visit_sequence = []
        self.bus_id = None  # ID du bus associé à cette route
        self.variables = {}  # Variables extraites d'AMPL
        self.etudiants_ramasses = {}  # Étudiants ramassés par lieu
        self.nb_etudiant_initial = []  # Nombre initial d'étudiants par lieu
        self.valid_itinerary = False  # Résultat de la validation de l'itinéraire
        self.all_students_picked = False  # Résultat de la vérification des étudiants
        self.valid_assignation = False  # Résultat de la vérification des assignations

    def evaluate(self):
        total_distance = 0
        dist_matrix = self.problem.get_dist_matrix()
        for i in range(len(self.visit_sequence) - 1):
            total_distance += dist_matrix[self.visit_sequence[i]][self.visit_sequence[i + 1]]
        return total_distance

    def validate(self):
        # Étape 1 : Vérifier si la séquence est valide (non vide et cohérente)
        if not self.visit_sequence:
            self.valid_itinerary = False
        pass

    def __str__(self):
        pass