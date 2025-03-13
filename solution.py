import sys

class Solution:
    def __init__(self):
        pass

    def evaluate(self):
        if self.validate() == False:
        # TODO Ajouter le code pour calculer la valeur de la fonction objectif dans les classes dérivées
        # On suppose que la valeur doit être minimisé
        # Par défaut nous remétons donc la plus grande valeur possible
        # un nombre a virgule flottante
       
            return sys.float_info.max
    
    def validate(self):
        # TODO Ajouter le code pour vérifier si une solution est réalisable dans les classes dérivées
        #Pour l'instant nous avons une solution vide que nous considérons toujours non-réalisable
        ###Le code ??
        # locations_list = list(range(0, self.problem.count_locations()))
        # if sorted(self.visit_sequence) == locations_list:
        #     return True
        # ici on valide quon a fait tout les lieux dans visit_sequence
        return False 