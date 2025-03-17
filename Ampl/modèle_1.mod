# ENSEMBLES
set L; # Ensemble des lieux
set B; # Ensemble de bus

# PARAMÈTRES
param n := card(L); # Nombre de lieux
param d {L, L} >= 0; # Matrice des distances
param nb_etudiant {L} >= 0; # Étudiants à chaque lieu
param cap_bus {B}; 
param total_etudiants := sum {i in L} nb_etudiant[i];
param M := 2 * n; # Big-M pour désactiver les contraintes de sous-tours lorsque nécessaire

# VARIABLES DE DÉCISION
var deplacement {L, L, B} binary; # x[i, j, b] = 1 si on voyage de i à j avec le bus b
var u {L, B} >= 0, <= n; # Permettre u[i, b] = 0 pour les lieux non assignés
var assignation {L, B} binary; # assignation[l, b] = 1 si le lieu l est assigné au bus b
var nb_etudiant_dans_bus {B} >= 0;

# FONCTION OBJECTIF : MINIMISER LE DÉPLACEMENT TOTAL
minimize Distance_Totale:
    sum {i in L, j in L, b in B: i != j} d[i, j] * deplacement[i, j, b];

# CONTRAINTES

### GESTION DES ASSIGNATIONS ###
# Chaque lieu intermédiaire est assigné à exactement un bus
subject to 1bus_Par_Lieu {i in L: i != 0}:
    sum {b in B} assignation[i, b] = 1;
    
# Obliger le départ (lieu 0) 
subject to Assign_Depart {b in B}:
    assignation[0, b] = 1;

#subject to Assign_Arrivee {b in B}:
    #assignation[2, b] = 1;  # Optionnel maintenant

### GESTION DES ARCS ET DES FLUX ###
# Un arc sortant du lieu 0 pour chaque bus (facultatif)
#subject to Depart_Entreprise {b in B}:
    #sum {j in L: j != 0} deplacement[0, j, b] <= 1;

# Aucun arc entrant au lieu 0 (gardé strict)
#subject to No_into_0 {b in B}:
    #sum {i in L: i != 0} deplacement[i, 0, b] = 0;

# 
subject to Depart_Ecole {b in B}:
    sum {j in L: j != 0} deplacement[0, j, b] = 1;
    
# Un arc entrant au lieu 2 pour chaque bus (facultatif)
subject to Arrivee_Ecole {b in B}:
    sum {i in L: i != 0} deplacement[i, 0, b] = 1;

# Aucun arc sortant du lieu 2 (gardé strict)
#subject to No_out_from_2 {b in B}:
    #sum {j in L: j != 2} deplacement[2, j, b] = 0;

# Conservation du flot pour les lieux intermédiaires
subject to One_in {j in L, b in B: j != 0}:  # Exclure le lieu d'arrivée (0)
    sum {i in L: i != j} deplacement[i, j, b] = assignation[j, b];

subject to One_out {i in L, b in B: i != 0}:  # Exclure le lieu d'arrivée (0)
    sum {j in L: i != j} deplacement[i, j, b] = assignation[i, b];

# Pas de boucles sur soi-même
subject to No_self_loop {b in B, i in L}:
    deplacement[i, i, b] = 0;

### ÉLIMINATION DES SOUS-TOURS ###
# Fixer le départ et l’arrivée dans l’ordre de visite (facultatif)
subject to depart_sequence {b in B}:
    u[0, b] = 1;

#subject to fini_a_ecole {b in B}:
    #u[2, b] <= n;

# Contrainte d’élimination des sous-tours (MTZ) avec big-M
subject to Subtour_Elimination {i in L, j in L, b in B: i != j and j != 0}:
    u[i, b] - u[j, b] + n * deplacement[i, j, b] <= (n - 1) + M * (2 - assignation[i, b] - assignation[j, b]);

# Mettera u=0 si le bus ne passe pas a un lieux
subject to U_If_Not_Assigned {i in L, b in B: i !=0}:
    u[i, b] <= n * assignation[i, b];

### GESTION DES BUS ET DES ÉLÈVES ###
# Capacité des bus
subject to capacite_bus {b in B}:
    sum {i in L} nb_etudiant[i] * assignation[i, b] <= cap_bus[b];

# Lien entre déplacement et assignation
subject to lien_deplacement_assignation_1 {i in L, j in L, b in B: i != j}:
    deplacement[i, j, b] <= assignation[i, b];

subject to lien_deplacement_assignation_2 {i in L, j in L, b in B: i != j}:
    deplacement[i, j, b] <= assignation[j, b];

# Calcul du nombre d’étudiants par bus
subject to cb_etudiant_ds_bus {b in B}:
    nb_etudiant_dans_bus[b] = sum {i in L: i != 0} (assignation[i, b] * nb_etudiant[i]);