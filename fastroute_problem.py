import problem as prob
import copy

class FastRouteProb(prob.Problem):
    def __init__(self, dist_matrices, lieux, nb_etudiant, buses=None, vitesse_moyenne=50):
        super(FastRouteProb, self).__init__()
        self._dist_matrices = copy.deepcopy(dist_matrices)  # Liste des matrices pour les différentes instances
        self._lieux = copy.deepcopy(lieux)
        self._nb_etudiant = copy.deepcopy(nb_etudiant)
        self._buses = buses if buses else []  # Liste d'objets Bus
        self._vitesse_moyenne = vitesse_moyenne  # Vitesse moyenne en km/h

    def count_locations(self):
        return len(self._dist_matrices[0]) if self._dist_matrices else 0

    def get_dist_matrix(self, instance_idx=0):
        return self._dist_matrices[instance_idx] if instance_idx < len(self._dist_matrices) else []

    def get_lieux(self):
        return self._lieux

    def get_nb_etudiant(self):
        return self._nb_etudiant

    def get_buses(self):
        return self._buses

    def get_vitesse_moyenne(self):
        return self._vitesse_moyenne

    def __str__(self):
        tmp_str = ''
        for idx, dist_matrix in enumerate(self._dist_matrices):
            tmp_str += f"Instance {idx + 1}:\n"
            for a_list in dist_matrix:
                tmp_str = tmp_str + ', '.join([str(i) for i in a_list])
                tmp_str = tmp_str + '\n'
        return str(tmp_str)