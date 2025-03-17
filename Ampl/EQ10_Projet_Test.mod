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
param cout_km {B};
param cout_mise_en_route {B};
param vitesse_moyenne;
param temps_arrive;

# VARIABLES DE DÉCISION
var deplacement {L, L, B} binary; # x[i, j, b] = 1 si on voyage de i à j avec le bus b
var u {L, B} >= 0, <= n; # Permettre u[i, b] = 0 pour les lieux non assignés
var assignation {L, B} binary; # assignation[l, b] = 1 si le lieu l est assigné au bus b
var nb_etudiant_dans_bus {B} >= 0;
var utilise_bus {B} binary; # 1 si le bus est utilisé, 0 sinon
var u_max {b in B} >= 0, <= n; # Variable auxiliaire pour le maximum de u[i, b]
var temps {L, L, B};

# FONCTION OBJECTIF : MINIMISER LE DÉPLACEMENT TOTAL
#minimize Distance_Totale:
    #sum {i in L, j in L, b in B: i != j} d[i, j] * deplacement[i, j, b];

minimize Distance_Totale:
    sum {i in L, j in L, b in B: i != j} d[i, j] * deplacement[i, j, b] * cout_km[b] + sum {b in B} cout_mise_en_route[b] * utilise_bus[b];

    
# CONTRAINTES
### GESTION DES ASSIGNATIONS ###
# Chaque lieu intermédiaire est assigné à exactement un bus
subject to 1bus_Par_Lieu {i in L: i != 0 and i != 1}:
    sum {b in B} assignation[i, b] = 1;
    
# Obliger le départ (lieu 0) 
subject to Assign_Depart {b in B}:
    assignation[0, b] = utilise_bus[b];

# Obliger le départ (lieu 0) seulement si le bus est utilisé
subject to Assign_Depart_si_bus {b in B}:
    assignation[0, b] >= utilise_bus[b] - (card(L) - 1) * (1 - utilise_bus[b]);

# Obliger l'arrivée (lieu 1)
subject to Assign_Arrivee {b in B}:
    assignation[1, b] = utilise_bus[b];

# Obliger l'arrivée (lieu 1) seulement si le bus est utilisé
subject to Assigne_Arrivee_si_bus {b in B}:
    assignation[1, b] >= utilise_bus[b] - (card(L) - 1) * (1 - utilise_bus[b]);

### GESTION DES ARCS ET DES FLUX ###
subject to Depart_Entreprise {b in B}:
    sum {j in L: j != 0} deplacement[0, j, b] <= utilise_bus[b];
    
subject to Depart_Entreprise_si_bus {b in B}:
    sum {j in L: j != 0} deplacement[0, j, b] >= utilise_bus[b] - (card(L) - 1) * (1 - utilise_bus[b]);
    
subject to Arrivee_Ecole {b in B}:
    sum {i in L: i != 1} deplacement[i, 1, b] <= utilise_bus[b];
    
subject to Arrivee_Ecole_si_bus {b in B}:
    sum {i in L: i != 1} deplacement[i, 1, b] >= utilise_bus[b] - (card(L) - 1) * (1 - utilise_bus[b]);

subject to One_in {j in L, b in B: j != 0 and j != 1}:
    sum {i in L: i != j} deplacement[i, j, b] = assignation[j, b];

subject to One_out {i in L, b in B: i != 0 and i != 1}:
    sum {j in L: i != j} deplacement[i, j, b] = assignation[i, b];

subject to No_self_loop {b in B, i in L}:
    deplacement[i, i, b] = 0;

### ÉLIMINATION DES SOUS-TOURS ###
subject to Depart_Sequence {b in B}:
    u[0, b] = utilise_bus[b];

subject to Define_u_max {i in L, b in B: i != 0 and i != 1}:
    u_max[b] >= u[i, b] - M * (1 - assignation[i, b]) - M * (1 - utilise_bus[b]);

subject to Arrivee_Sequence_ajustée {b in B}:
    u[1, b] >= (u_max[b] + 1) * utilise_bus[b] - M * (1 - utilise_bus[b]);
    
subject to Arrivee_Sequence_ajustée2 {b in B}:
	u[1, b] <= (u_max[b] + 1) * utilise_bus[b] + M * (1 - utilise_bus[b]);

# Contrainte originale remplacée
# subject to Arrivee_Sequence {b in B}:
#     u[1, b] >= (n - card(L) + 2) * utilise_bus[b];

subject to Subtour_Elimination {i in L, j in L, b in B: i != j and j != 0}:
    u[i, b] - u[j, b] + n * deplacement[i, j, b] <= (n - 1) + M * (2 - assignation[i, b] - assignation[j, b]);

subject to U_If_Not_Assigned {i in L, b in B: i != 0 and i != 1}:
    u[i, b] <= n * assignation[i, b];

# complète U_if_Not_Assigned, car si le bus n'était pas utilisée il allais à lÉcole quand mm dans la séquence de u
subject to U_If_Not_Assigned_Arrivee {b in B}:
    u[1, b] <= n * assignation[1, b];

### GESTION DES BUS ET DES ÉLÈVES ###
subject to capacite_bus {b in B}:
    sum {i in L} nb_etudiant[i] * assignation[i, b] <= cap_bus[b] * utilise_bus[b];

subject to lien_deplacement_assignation_1 {i in L, j in L, b in B: i != j}:
    deplacement[i, j, b] <= assignation[i, b];

subject to lien_deplacement_assignation_2 {i in L, j in L, b in B: i != j}:
    deplacement[i, j, b] <= assignation[j, b];

subject to cb_etudiant_ds_bus {b in B}:
    nb_etudiant_dans_bus[b] = sum {i in L: i != 0 and i != 1} (assignation[i, b] * nb_etudiant[i]);


### GESTION DES TEMPS/DÉLAI ###
subject to heure_arrive {b in B, i in L, j in L: i != j}:
	temps[i, j, b] = (deplacement[i, j, b] * d[i, j]) / vitesse_moyenne;

# Les élèves ne peut pas passer plus d'une heure pas semaine
#subject to temps_par_bus_avec_élèves {b in B}:
	#sum {i in L, j in L : i != j and i != 0} temps[i,j,b] <= 60;


    