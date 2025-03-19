import solution as sol

# Élève est une classe qui servira de valider si les étudiants sont rammassés
class Eleves(sol.Solution):
    def __init__(self, students_per_location):
        self.students_per_location = students_per_location # nb_etudiants1

    def evaluate(self, students_in_bus):
        """
        Vérifie que tous les étudiants ont été ramassés.L
        """
        total_picked_up = sum(students_in_bus)
        total_students = sum(self.students_per_location)
        return total_picked_up == total_students

    def validate(self, students_in_bus):
        """
        Calcule le nombre total d'étudiants ramassés par la solution AMPL.
        """
        return sum(students_in_bus.values())  # Retourne la somme des valeurs dans nb_etudiant_dans_bus

    def __str__(self):
        return f"Étudiants: {sum(self.students_per_location)} dans {len(self.students_per_location)} lieux"