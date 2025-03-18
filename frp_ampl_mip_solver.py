import solver
import fastroute_problem as frp
import route_solution as rsol
import amplpy
import os
import numpy as np
import pandas as pd
import bus as bus
import élève_solution as élève

class FrpAmplMipSolver(solver.Solver):
    def __init__(self):
        super().__init__()

    def solve(self, problem_instance: frp.FastRouteProb = None, Autobus= [], Étudiants: élève.Élève = None, vitesse_moyenne = None):
        if problem_instance is None:
            raise ValueError("Aucun problème n'a été fourni.")

        # Récupérer les paramètres depuis FastRouteProb
        n = problem_instance.count_locations()
        nombre_de_bus = len(Autobus)
        dist_matrix = problem_instance # une liste de liste
        Autobus = Autobus #Une liste d'objet bus'
        nb_etudiant_total = sum(Étudiant) # Une liste
        vitesse_moyenne = vitesse_moyenne

        # Calculer les paramètres dérivés
        total_etudiants = sum(nb_etudiant)
        M = 2 * n

        # Préparer les ensembles et paramètres pour AMPL
        L_values = [i for i in range(n)]
        B_values = [i for i in range(nombre_de_bus)]
        d_df = pd.DataFrame(dist_matrix, columns=L_values, index=L_values)
        cap_bus = {Autobus.id: Autobus.capacity for Autobus in Autobus}
        cout_km = {Autobus.id: Autobus.cost_per_km}
        cout_mise_en_route = {Autobus.id: Autobus.startup_cost}

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

        #Ici il faut filter les 0 dans u et que l'addition de toutes les en ordre =  la séquence de tous les lieux
        #Il faut aussi envoyer le nombre d'étudiants total dans la class élève pour qu'elle valide s'ils sont tous ramassés
        #Il faut envoyer le temps que ca a pris pour chaque bus dans classe bus pour calculer leur heure de départ
        #

        # Calculer le nombre d'étudiants ramassés par lieu
        # etudiants_ramasses = {l: 0 for l in L_values}
        # for (l, b), val in assignation_values.items():
        #     if val > 0:  # Si le lieu l est assigné au bus b
        #         etudiants_ramasses[l] += nb_etudiant[l] * val

        # # Définir les indices explicites pour l'entreprise et l'école
        # entreprise_idx = 0  # À ajuster si nécessaire dans votre problème
        # ecole_idx = 1  # À ajuster si nécessaire dans votre problème
        # problem_instance.entreprise_idx = entreprise_idx
        # problem_instance.ecole_idx = ecole_idx

        # # Extraire les séquences d'itinéraires à partir de u pour chaque bus
        # routes = []
        # for b in B_values:
        #     u_b = [(i, val) for (i, b_val), val in u_values.items() if b_val == b]
        #     all_zeros = all(val == 0 for _, val in u_b)
            
        #     if utilise_bus_values.get((b,), 0) == 1:  # Si le bus est utilisé
        #         if all_zeros:
        #             # Si toutes les valeurs sont 0, garder uniquement les zéros
        #             visit_sequence = [i for i, val in u_b]
        #         else:
        #             # Filtrer les zéros et trier par ordre de visite
        #             u_b_filtered = [(i, val) for i, val in u_b if val > 0]
        #             u_b_sorted = sorted(u_b_filtered, key=lambda x: x[1])
        #             visit_sequence = [item[0] for item in u_b_sorted]
        #     else:
        #         # Bus non utilisé : séquence vide
        #         visit_sequence = []

        #     # Créer une route pour ce bus
        #     route = rsol.Route(problem_instance)
        #     route.visit_sequence = visit_sequence
        #     route.bus_id = b
        #     route.variables = solution_data
        #     route.etudiants_ramasses = etudiants_ramasses
        #     route.nb_etudiant_initial = nb_etudiant
        #     routes.append(route)

        # return routes