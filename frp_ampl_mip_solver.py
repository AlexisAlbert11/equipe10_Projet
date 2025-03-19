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

    def solve(self, problem_instance: frp.FastRouteProb = None, Autobus = [], Étudiants: élève.Élève = None, vitesse_moyenne = None):
        if problem_instance is None:
            raise ValueError("Aucun problème n'a été fourni.")

        # Récupérer des paramêtres
        n = problem_instance.count_locations()
        nombre_de_bus = len(Autobus)
        dist_matrix = np.array(problem_instance._dist_matrix) # une liste de liste
        Autobus = Autobus #Une liste d'objet bus'
        nb_etudiant = [etudiant.nb_etudiant for etudiant in Étudiants] # Une liste
        vitesse_moyenne = vitesse_moyenne

        # Calculer les paramètres dérivés
        total_etudiants = sum(nb_etudiant)
        M = 2 * n

        # Préparer les ensembles et paramètres pour AMPL
        #SET
        L_values = [i for i in range(n)]
        B_values = [i for i in range(nombre_de_bus)]
        #param
        d_df = pd.DataFrame(dist_matrix, columns=L_values, index=L_values)
        cap_bus = {Autobus.id: Autobus.capacity for Autobus in Autobus}
        cout_km = {bus.id: bus.cost_per_km for bus in Autobus}
        cout_mise_en_route = {bus.id: bus.startup_cost for bus in Autobus}
        # Initialiser AMPL
        #ampl_path = os.path.normpath('C:/Users/ALALB18/AMPL')
        ampl_path = os.path.normpath('C:/AMPL')
        ampl_env = amplpy.Environment(ampl_path)
        ampl = amplpy.AMPL(ampl_env)

        # Configurer AMPL
        ampl.setOption('solver', 'gurobi')
        ampl.setOption('gurobi_options', f'timelim {self.max_time_sec} outlev 1')

        # Charger le modèle AMPL Alex
        # model_dir = os.path.normpath('C:/equipe10_Projet/Ampl')
        # ampl.read(os.path.join(model_dir, 'EQ10_Projet_Test.mod'))
        #Charger Joel
        model_dir = os.path.normpath('D:/SIAD/Projet session/Python/Ampl')
        ampl.read(os.path.join(model_dir, 'EQ10_Projet_Test.mod'))
        # Définir les ensembles
        ampl.set["L"] = L_values
        ampl.set["B"] = B_values

        # Définir les paramètres
        ampl.param["d"] = d_df
        ampl.param["nb_etudiant"] = pd.Series(nb_etudiant, index=L_values)
        ampl.param["cap_bus"] = cap_bus
        ampl.param["cout_km"] = cout_km
        ampl.param["cout_mise_en_route"] = cout_mise_en_route
        ampl.param["vitesse_moyenne"] = vitesse_moyenne

        # Résoudre le modèle
        ampl.solve()


        #
        u_values = ampl.getVariable("u").getValues().toList()
        # Variable deplacement
        d_values = ampl.getVariable("deplacement").getValues().toList()
        # Valeur de deplacement par autobus
        distance_bus = ampl.getVariable("d_bus").getValues().toList()
        
        
        ### TRAITEMENT/TRANSFORMATION DE LA VARIABLE U ###
        liste_voyage_bus = []
        ordre_bus_liste = []
        
        
        for x, y, z in u_values: # Création d'une liste avec les déplacement fait (On laisse de côté les tuples qui représentent zéro déplacement)
            if z != 0:
                liste_voyage_bus.append((x, y, z))
            else:
                continue


        ###    PREPARATION  POUR VALIDATE DE ROUTE    ###


        bus_dict = {}        # Création d'un dictionnaire vide

        # Remplissage du dictionnaire
        for ville, bus, ordre in liste_voyage_bus:
            if bus not in bus_dict:
                bus_dict[bus] = []  # On ajoute d'une liste si bus n'est pas dedans
            bus_dict[bus].append((ordre, ville))  # Remplis la liste qui vient d'etre créer avec u et la ville

        # Trier les villes pour chaque autobus selon l'ordre de visite
        for bus in bus_dict:
            bus_dict[bus].sort()  # Sert a trier selon les ordre (le premier élement)

        # Affichage des résultats
        for bus in sorted(bus_dict):  # Trie les bus par numéro
            villes_triees = [ville for _, ville in bus_dict[bus]]  # Extraire les villes triées
            print(f"Autobus {bus}: {villes_triees}")
            ordre_bus_liste.append(villes_triees)
        
        liste_de_verification01 = [0, 1] # Parce que c'est aussi vérifier que les bus passent par 0,1 
        for sous_liste in ordre_bus_liste:
        # Parcours de chaque nombre dans la sous-liste
            for num in sous_liste:
        # Vérification que le nombre n'est ni 0 ni 1
                if num not in (0, 1):
            # Ajout du nombre à la liste filtrée
                    liste_de_verification01.append(num)

        # Tri de la liste obtenue
        liste_de_verification01.sort()

        ##      Calcul des distances totales parcourues      ##

        somme_des_distances = 0
        for x, y, z, k in d_values: 
                somme_des_distances += k *problem_instance._dist_matrix[x][y]
        print(somme_des_distances)
        
        

        ###  Afficher les valeurs récupérées ###

        #print("\nValeurs de u récupérées depuis AMPL :")
        #print(type(u_values))
        #print(u_values)
        #print(liste_voyage_bus)
        #print("ICI YAYA")
        #print(ordre_bus_liste)
        #print(liste_de_verification01)
        #print("DEPLACEMENT")
        #print(d_values)
        print(distance_bus)



        #Test de validation route
        Route = rsol.Route(problem_instance)
        Route.depart_fin =ordre_bus_liste
        Route.visit_sequence = liste_de_verification01
        return Route 

        #Test de bus



        #Test de élève
        

         

        