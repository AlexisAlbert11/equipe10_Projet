import solution as sol
import bus as bus
import fastroute_problem as frp


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
        pass