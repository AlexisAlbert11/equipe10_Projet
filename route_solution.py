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
        else:
            self.valid_itinerary = True  # On assume que solve a déjà trié correctement

        # Si pas de variables, on ne peut pas valider davantage
        if not self.variables or not self.etudiants_ramasses or not self.nb_etudiant_initial:
            self.all_students_picked = False
            self.valid_assignation = False
            return self.valid_itinerary

        # Récupérer les données nécessaires
        assignation = self.variables.get('assignation', {})
        n = self.problem.count_locations()
        B_values = [bus.id for bus in self.FastRouteProb.get_buses()]
        
        # Hypothèse : lieu 0 = entreprise, dernier lieu (n-1) = école
        entreprise = 0
        ecole = n - 1  # À ajuster si l'école a un autre index spécifique dans votre problème

        # Étape 2 : Vérifier que tous les étudiants sont ramassés
        total_initial = sum(self.nb_etudiant_initial)
        total_ramasses = sum(self.etudiants_ramasses.values())
        self.all_students_picked = (total_ramasses == total_initial)

        # Étape 3 : Vérifier que chaque lieu (sauf entreprise et école) est assigné à un seul bus
        self.valid_assignation = True
        assignation_count = {l: 0 for l in range(n)}  # Compte le nombre d'assignations par lieu
        for (l, b), val in assignation.items():
            if val > 0:  # Si le lieu l est assigné au bus b
                assignation_count[l] += 1
        
        # Vérifier les assignations pour chaque lieu
        for l in range(n):
            if l != entreprise and l != ecole:  # Exclure entreprise et école
                if assignation_count[l] != 1:  # Doit être assigné exactement une fois
                    self.valid_assignation = False
                    break
            # Les lieux entreprise et école peuvent être assignés à plusieurs bus (ou pas de restriction)

        # Retourner True si toutes les conditions sont remplies
        return self.valid_itinerary and self.all_students_picked and self.valid_assignation

    def __str__(self):
        validity_message = "valide" if self.valid_itinerary else "invalide"
        students_message = "tous les étudiants ramassés" if self.all_students_picked else "tous les étudiants NON ramassés"
        assignation_message = "assignations valides" if self.valid_assignation else "assignations invalides"
        return (f"Bus {self.bus_id} - Itinéraire {validity_message}: {self.visit_sequence}, "
                f"Distance: {self.evaluate()}, {students_message}, {assignation_message}")