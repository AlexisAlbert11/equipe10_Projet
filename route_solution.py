import solution as sol
import sys

class Route(sol.Solution):
    def __init__(self, solvedProblem=frp.FastRouteProb()):
        super(Route, self).__init__()
        self.visit_sequence = []
        self.depart_fin = []
        self.problem = solvedProblem
        

    def evaluate(self):
        if self.validate()== False:
       
            raise ("Validation de route a échoué")
        else:
            print("Validation de route réussis")

    def validate(self):
        locations_list = list(range(0, self.problem.count_locations()))
        
        # Vérification que tous les lieux sont visités dans l'ordre attendu
        if self.visit_sequence != locations_list:
            return False
        
        # Vérification de toutes les listes dans depart_fin
        for route in self.depart_fin:
            if not (route[0] == 0 and route[-1] == 1):  # Vérifie que chaque route commence à 0 et finit à 1
                return False

        return True  # Si toutes les routes sont valides

    def __str__(self):
        tmp_str = ""
        for bus, seq in self.visit_sequences.items():
            if seq:  # Ne pas afficher les bus sans séquence
                tmp_str += f"Bus {bus}: {', '.join(str(i) for i in seq)}\n"
        return tmp_str.strip()

    def validate(self):
        """
        Vérifie que l'ensemble des séquences couvre tous les lieux (0 à n-1) exactement une fois.
        """
        all_locations = set()
        for seq in self.visit_sequences.values():
            all_locations.update(seq)
        expected_locations = list(range(self.problem.count_locations()))
        return sorted(all_locations) == expected_locations

    def evaluate(self):
        """
        Calcule la somme des distances parcourues par tous les bus.
        Retourne sys.float_info.max si la solution n'est pas valide.
        """
        if not self.validate():
            return sys.float_info.max

        obj_val = 0
        for seq in self.visit_sequences.values():
            if seq:  # Ignorer les séquences vides
                for i in range(len(seq) - 1):
                    curr_source = seq[i]
                    curr_destination = seq[i + 1]
                    curr_distance = self.problem._dist_matrix[curr_source][curr_destination]
                    obj_val += curr_distance
        return obj_val
