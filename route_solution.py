import solution as sol

class Route(sol.Solution):
    def __init__(self, problem):
        super().__init__(problem)
        self.visit_sequence = []
        self.bus_id = None  # ID du bus associé à cette route
        self.variables = {}  # Variables extraites d'AMPL
        self.valid_itinerary = False  # Résultat de la validation de l'itinéraire
        self.all_students_picked = False  # Résultat de la vérification des étudiants

    def evaluate(self):
        total_distance = 0
        dist_matrix = self.problem.get_dist_matrix()
        for i in range(len(self.visit_sequence) - 1):
            total_distance += dist_matrix[self.visit_sequence[i]][self.visit_sequence[i + 1]]
        return total_distance

    def validate(self):
        # Étape 1 : Vérifier si la séquence est croissante en ignorant les zéros après le premier
        if not self.visit_sequence:
            self.valid_itinerary = False
        else:
            # Filtrer les zéros : garder le premier 0 comme point de départ, ignorer les autres
            filtered_sequence = []
            first_zero_seen = False
            for loc in self.visit_sequence:
                if loc == 0 and not first_zero_seen:
                    filtered_sequence.append(loc)
                    first_zero_seen = True
                elif loc != 0:
                    filtered_sequence.append(loc)

            # Vérifier si la séquence filtrée est croissante
            if not filtered_sequence:
                self.valid_itinerary = False
            else:
                self.valid_itinerary = True
                for i in range(len(filtered_sequence) - 1):
                    if filtered_sequence[i] > filtered_sequence[i + 1]:
                        self.valid_itinerary = False
                        break

        # Étape 2 : Vérifier si tous les étudiants ont été ramassés
        if not self.variables:
            self.all_students_picked = False
            return self.valid_itinerary

        # Récupérer les données nécessaires
        assignation = self.variables.get('assignation', {})
        nb_etudiant = self.problem.get_nb_etudiant()
        total_etudiants = sum(nb_etudiant)

        # Calculer le nombre total d'étudiants ramassés
        total_assigned_students = 0
        n = self.problem.count_locations()
        B_values = [bus.id for bus in self.problem.get_buses()]
        for b in B_values:
            for i in range(n):
                if assignation.get((i, b), 0) == 1:
                    total_assigned_students += nb_etudiant[i]

        # Vérifier si tous les étudiants ont été ramassés
        self.all_students_picked = (total_assigned_students == total_etudiants)

        return self.valid_itinerary and self.all_students_picked

    def __str__(self):
        validity_message = "valide" if self.valid_itinerary else "invalide"
        students_message = "tous les étudiants ramassés" if self.all_students_picked else "tous les étudiants NON ramassés"
        return (f"Bus {self.bus_id} - Itinéraire {validity_message}: {self.visit_sequence}, "
                f"Distance: {self.evaluate()}, {students_message}")