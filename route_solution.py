import solution as sol
import sys

class Route(sol.Solution):
    def __init__(self, solvedProblem):
        super(Route, self).__init__()
        self.visit_sequences = {}  # Dict {bus: liste des lieux visités}
        self.problem = solvedProblem  # Instance de FastRouteProb

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
