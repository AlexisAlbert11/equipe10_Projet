import problem as prob
import copy

class FastRouteProb(prob.Problem):
    def __init__(self, dist_matrix= [[]]):
        super(FastRouteProb, self).__init__()
        self._dist_matrix = copy.deepcopy(dist_matrix)  # Liste de la matrice pour les différentes instances

    def count_locations(self):
        return len(self._dist_matrix)

    def __str__(self):
        tmp_str = ''
        
        for a_list in self._dist_matrix:
            tmp_str = tmp_str + ', '.join([str(i) for i in a_list])
            tmp_str = tmp_str + '\n'
        return str(tmp_str)