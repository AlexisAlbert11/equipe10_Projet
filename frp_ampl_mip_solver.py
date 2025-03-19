import solver
import fastroute_problem as frp
import route_solution as rsol
import amplpy
import os
import numpy as np
import pandas as pd
import bus as bus
import élève_solution as élève
import busfleet_bus as bfleet

class FrpAmplMipSolver(solver.Solver):
    def __init__(self):
        super().__init__()

    def solve(self, problem: frp.FastRouteProb, bus_fleet: bfleet.BusFleet, eleves: élève.Eleves):
        if problem is None or bus_fleet is None or eleves is None:
            raise ValueError("Aucun problème n'a été fourni.")
        
        # Configuration de l'environnement AMPL
        ampl_path = os.path.normpath('C:/Users/ALALB18/AMPL')
        ampl_env = amplpy.Environment(ampl_path)
        ampl = amplpy.AMPL(ampl_env)

        ampl.setOption('solver', 'cbc')
        ampl.setOption('gurobi_options', 'timelim 10 outlev 1')

        # Chemin du modèle
        model_dir = os.path.normpath('C:/equipe10_Projet/Ampl')
        ampl.read(os.path.join(model_dir, 'EQ10_Projet_Test.mod'))

        # Définir les ensembles
        L_values = [i for i in range(problem.count_locations())]
        B_values = [i for i in range(len(bus_fleet.buses))]
        ampl.set["L"] = L_values
        ampl.set["B"] = B_values

        # Définir les paramètres avec pandas pour d et nb_etudiant
        matrice = np.array(problem._dist_matrix)
        d_df = pd.DataFrame(matrice, columns=L_values, index=L_values)
        etudiant_df = pd.DataFrame([eleves.students_per_location[i] for i in L_values], index=L_values)
        
        ampl.param["d"] = d_df
        ampl.param["nb_etudiant"] = etudiant_df

        # Définir les paramètres des bus à partir de bus_fleet.buses
        ampl.param["cap_bus"] = {b: bus_fleet.buses[b].capacity for b in B_values}
        ampl.param["cout_km"] = {b: bus_fleet.buses[b].cost_per_km for b in B_values}
        ampl.param["cout_mise_en_route"] = {b: bus_fleet.buses[b].startup_cost for b in B_values}
        ampl.param["vitesse_moyenne"] = bus_fleet.avg_speed

        # Résoudre
        ampl.solve()

        # Récupérer les variables
        u = ampl.var["u"].getValues().toDict()
        assignation = ampl.var["assignation"].getValues().toDict()
        nb_etudiant_dans_bus = ampl.var["nb_etudiant_dans_bus"].getValues().toDict()
        temps = ampl.var["temps"].getValues().toDict()

        # Construire les séquences à partir de u
        sequences = {}
        for b in B_values:
            seq = [i for (i, bus_idx) in u.keys() if bus_idx == b and u[(i, bus_idx)] > 0]
            sequences[b] = sorted(seq, key=lambda x: u[(x, b)])

        # Créer une instance de Route et lui assigner les séquences
        route_instance = rsol.Route(problem)
        route_instance.visit_sequences = sequences

        # Assigner assignation à bus_fleet (Option 2)
        bus_fleet.set_assignation(assignation)

        # Retourner les résultats
        return {
            "route": route_instance,
            "assignation": assignation,  # Toujours renvoyé pour compatibilité
            "nb_etudiant_dans_bus": nb_etudiant_dans_bus,
            "temps": temps
        }
    
