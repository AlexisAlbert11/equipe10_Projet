import coordinates as co


#Test initiaux avant utilisation du API et Excel
#coordonnées = co.Coordinates([[(1, 2)], [(3, 4)]], ["A", "B"])
#print(coordonnées)
#coordonnées.get_all_coordinates()


#Test Coordinates à faire (((((C'EST 5$ À CHAQUE TEST AVEC GOOGLE, ON A 430$ DE GRATUIT DURANT 3 MOIS PAR COMPTE)))))
#ALORS NE PAS FAIRE LES FOUS
fichier_excel = "C:\\equipe10_Projet\\Data.xlsx"  # Chemin corrigé avec double backslash ou barre oblique
coordonnees = co.Coordinates(fichier_excel=fichier_excel)
print(coordonnees)
distance_matrix = coordonnees.create_distance_matrix()
print("Matrice de distances :")
for row in distance_matrix:
    print(row)
