import solver
import fastroute_problem as frp
import route_solution as rsol
import amplpy
import os
import numpy as np
import pandas as pd

class FrpAmplMipSolver(solver.Solver):
    def __init__(self):
        super().__init__()

    def solve(self, problem_instance: frp.FastRouteProb = None):
        if problem_instance is None:
            raise ValueError("Aucun problème n'a été fourni.")

        # Récupérer les paramètres depuis FastRouteProb
        n = problem_instance.count_locations()
        dist_matrix = problem_instance.get_dist_matrix(instance_idx=0)
        lieux = problem_instance.get_lieux()
        nb_etudiant = problem_instance.get_nb_etudiant()
        buses = problem_instance.get_buses()
        vitesse_moyenne = problem_instance.get_vitesse_moyenne()

        # Calculer les paramètres dérivés
        total_etudiants = sum(nb_etudiant)
        M = 2 * n

        # Préparer les ensembles et paramètres pour AMPL
        L_values = [i for i in range(n)]
        B_values = [bus.id for bus in buses]
        d_df = pd.DataFrame(dist_matrix, columns=L_values, index=L_values)
        cap_bus = {bus.id: bus.capacity for bus in buses}
        cout_km = {bus.id: bus.cost_per_km for bus in buses}
        cout_mise_en_route = {bus.id: bus.startup_cost for bus in buses}

        # Initialiser AMPL
        ampl_path = os.path.normpath('C:/Users/ALALB18/AMPL')
        ampl_env = amplpy.Environment(ampl_path)
        ampl = amplpy.AMPL(ampl_env)

        # Configurer AMPL
        ampl.setOption('solver', 'gurobi')
        ampl.setOption('gurobi_options', f'timelim {self.max_time_sec} outlev 1')

        # Charger le modèle AMPL
        model_dir = os.path.normpath('C:/equipe10_Projet/Ampl')
        ampl.read(os.path.join(model_dir, 'EQ10_Projet_Test.mod'))

        # Définir les ensembles
        ampl.set["L"] = L_values
        ampl.set["B"] = B_values

        # Définir les paramètres
        ampl.param["n"] = n
        ampl.param["d"] = d_df
        ampl.param["nb_etudiant"] = pd.Series(nb_etudiant, index=L_values)
        ampl.param["cap_bus"] = cap_bus
        ampl.param["total_etudiants"] = total_etudiants
        ampl.param["M"] = M
        ampl.param["cout_km"] = cout_km
        ampl.param["cout_mise_en_route"] = cout_mise_en_route
        ampl.param["vitesse_moyenne"] = vitesse_moyenne

        # Résoudre le modèle
        ampl.solve()

        # Récupérer toutes les variables
        solution_data = {}
        deplacement_values = ampl.getVariable('deplacement').getValues().toDict()
        solution_data['deplacement'] = deplacement_values
        u_values = ampl.getVariable('u').getValues().toDict()
        solution_data['u'] = u_values
        assignation_values = ampl.getVariable('assignation').getValues().toDict()
        solution_data['assignation'] = assignation_values
        nb_etudiant_dans_bus_values = ampl.getVariable('nb_etudiant_dans_bus').getValues().toDict()
        solution_data['nb_etudiant_dans_bus'] = nb_etudiant_dans_bus_values
        utilise_bus_values = ampl.getVariable('utilise_bus').getValues().toDict()
        solution_data['utilise_bus'] = utilise_bus_values
        u_max_values = ampl.getVariable('u_max').getValues().toDict()
        solution_data['u_max'] = u_max_values
        temps_values = ampl.getVariable('temps').getValues().toDict()
        solution_data['temps'] = temps_values

        # Extraire les séquences d'itinéraires à partir de u pour chaque bus
        routes = []
        for b in B_values:
            if utilise_bus_values.get((b,), 0) == 1:  # Si le bus est utilisé
                u_b = [(i, val) for (i, b_val), val in u_values.items() if b_val == b]
                u_b_sorted = sorted(u_b, key=lambda x: x[1] if x[1] > 0 else float('inf'))
                visit_sequence = [item[0] for item in u_b_sorted if item[1] > 0]

                # Créer une route pour ce bus
                route = rsol.Route(problem_instance)
                route.visit_sequence = visit_sequence
                route.bus_id = b  # Ajouter l'ID du bus à la route
                route.variables = solution_data  # Stocker toutes les variables AMPL dans la route
                routes.append(route)

        return routes