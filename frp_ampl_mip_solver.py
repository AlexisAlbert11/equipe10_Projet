import solver
import fastroute_problem as frp
import route_solution as rsol


import amplpy #AJOUT
import os # AJOUT
import numpy as np # AJOUT
import pandas as pd # AJOUT


class FrpAmplMipSolver(solver.Solver):

    def __init__(self):
        super().__init__()
        
        
    #SOLVE sert a instancier AMPL de la question 2 
    def solve(self, problem_instance:frp.FastRouteProb=None):
        
        if problem_instance is None:
            raise ValueError("Aucun problème n'a été fourni.")
        
        matrice = np.array(problem_instance._dist_matrix)

        #ampl_env = amplpy.Environment()
        #alexis
        ampl_path = os.path.normpath('C:/Users/ALALB18/AMPL')
        ampl_env = amplpy.Environment(ampl_path)
        #Joel
        # ampl_path = os.path.normpath('C:/AMPL')
        # ampl_env = amplpy.Environment(ampl_path)

        ampl = amplpy.AMPL(ampl_env)

        #Limiter le temps d'exécution à 10sec
        ampl.setOption('solver', 'gurobi')
        ampl.setOption('gurobi_options', f'timelim {self.max_time_sec} outlev 1')
        #alexis
        model_dir = os.path.normpath('C:/Travail-en-quipe-de-2-2/equipe10_TP_1')
        ampl.read(os.path.join(model_dir, 'Q_3_SIAD 1.mod'))
        #Joel
        # model_dir = os.path.normpath('D:/SIAD/Solveur Q3')
        # ampl.read(os.path.join(model_dir, 'Q_3_SIAD.mod'))

        L_values = [i for i in range(problem_instance.count_locations())]
        
        d_df = pd.DataFrame(matrice, columns=L_values, index=L_values)

        ampl.set["L"] = L_values

        ampl.param["d"] = d_df

        ampl.solve()

        itinéraire = ampl.getVariable('u').getValues().toList()
        
        itinéraire_classé = sorted(itinéraire, key=lambda x: x[1])
        itinéraire_final=[]

        for lieu in itinéraire_classé:
            itinéraire_final.append(lieu[0])

        Route = rsol.Route(problem_instance)
        Route.visit_sequence = itinéraire_final
        return Route