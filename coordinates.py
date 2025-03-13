import copy
import googlemaps
from googlemaps.exceptions import ApiError, TransportError, Timeout
import pandas as pd

class Coordinates:
    def __init__(self, coordinates_matrix=[[]], lieux=None, fichier_excel=None, sheet_name=0):
        """
        Initialise une instance de Coordinates soit avec une matrice et des noms de lieux,
        soit en lisant directement depuis un fichier Excel.
        Args:
            coordinates_matrix (list, optional): Matrice de coordonnées (défaut: [[]]).
            lieux (list, optional): Liste des noms de lieux (défaut: None).
            fichier_excel (str, optional): Chemin vers le fichier Excel (défaut: None).
            sheet_name (str or int, optional): Nom ou index de la feuille à lire (défaut: 0).
        """
        # Si fichier_excel est fourni, lire les données depuis Excel
        if fichier_excel:
            lieux, coordinates_matrix = self.lire_excel(fichier_excel, sheet_name)

        self._coordinates_matrix = copy.deepcopy(coordinates_matrix)
        self._lieux = lieux if lieux else [f"Lieu {i+1}" for i in range(len(coordinates_matrix))]
        self._gmaps = googlemaps.Client(key='AIzaSyAEhvDXHeWZwqrDpHWyK_RMf-bauWfioQ0')

    def lire_excel(self, fichier_excel, sheet_name):
        """
        Lit les coordonnées depuis un fichier Excel (colonnes C, D, E, lignes 2 à 34).
        Args:
            fichier_excel (str): Chemin vers le fichier Excel.
            sheet_name (str or int): Nom ou index de la feuille à lire.
        Returns:
            tuple: (liste de noms de lieux, matrice de coordonnées).
        """
        # Lire les colonnes C, D, E (indices 2, 3, 4) et les lignes 2 à 34
        df = pd.read_excel(fichier_excel, sheet_name=sheet_name, 
                          usecols=[2, 3, 4],  # Colonnes C, D, E
                          skiprows=1,          # Ignorer la ligne 1 (en-têtes)
                          nrows=33)            # Lire 33 lignes (de 2 à 34)

        # Extraire les données
        lieux = df.iloc[:, 0].tolist()  # Colonne C (Nom du quartier)
        latitudes = df.iloc[:, 1].tolist()  # Colonne D (Latitude)
        longitudes = df.iloc[:, 2].tolist()  # Colonne E (Longitude)
        
        # Créer une liste de coordonnées (tuples)
        coordinates = [(lat, lon) for lat, lon in zip(latitudes, longitudes)]
        
        # Créer la matrice de coordonnées
        coordinates_matrix = [[coord] for coord in coordinates]
        
        return lieux, coordinates_matrix

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de la matrice de coordonnées.
        Chaque ligne représente un lieu avec ses coordonnées absolues (tuples).
        Returns:
            str: Une chaîne formatée représentant la matrice avec des étiquettes de lieux.
        """
        if not self._coordinates_matrix or all(not row for row in self._coordinates_matrix):
            return "Matrice de coordonnées vide"

        n_rows = len(self._coordinates_matrix)
        if len(self._lieux) != n_rows:
            return "Erreur : Le nombre de noms de lieux ne correspond pas au nombre de lignes"

        # Vérifier que chaque ligne contient exactement une coordonnée (tuple)
        for row in self._coordinates_matrix:
            if not row or not isinstance(row, list) or len(row) != 1 or not isinstance(row[0], tuple):
                return "Erreur : Chaque ligne doit contenir exactement un tuple de coordonnées"

        lieu_noms = self._lieux
        max_width = max(len(str(row[0])) for row in self._coordinates_matrix) + 2
        max_label_width = max(len(label) for label in lieu_noms) + 2

        # Construction de la chaîne
        lignes = []
        # Ligne d'en-tête
        header = " " * max_label_width + "Coordonnées"
        lignes.append(header)

        # Lignes de la matrice
        for i in range(n_rows):
            row_str = f"{lieu_noms[i]:<{max_label_width}}" + f"{str(self._coordinates_matrix[i][0]):>{max_width}}"
            lignes.append(row_str)

        return "\n".join(lignes)
    
    def get_all_coordinates(self):
        all_coordinates = []
        for row in self._coordinates_matrix:
            if not isinstance(row, list) or len(row) != 1 or not isinstance(row[0], tuple):
                continue
            all_coordinates.append(row[0])
        return all_coordinates
    
    def create_distance_matrix(self):
        """
        Crée une matrice de distances entre toutes les paires de coordonnées en utilisant l'API Google Maps.
        Les distances sont retournées en kilomètres.
        Returns:
            list: Une matrice 2D où distance[i][j] est la distance routière (en kilomètres) entre les coordonnées i et j.
        """
        coords = self.get_all_coordinates()
        n = len(coords)
        
        if n == 0:
            return [[]]  # Retourne une matrice vide si aucune coordonnée
        
        # Initialisation de la matrice avec des zéros
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Appel à l'API Google Maps pour toutes les paires
        try:
            # Préparer les origines et destinations
            origins = [(lat, lon) for lat, lon in coords]
            destinations = origins

            # Appel à l'API Distance Matrix
            matrix_response = self._gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode="driving",
                units="metric"
            )

            # Vérifier le statut de la réponse
            if matrix_response['status'] != 'OK':
                raise ValueError(f"Erreur de l'API Google Maps : {matrix_response['status']}")

            # Parcourir les résultats et convertir les distances en kilomètres
            for i in range(n):
                row = matrix_response['rows'][i]['elements']
                for j in range(n):
                    element = row[j]
                    if element['status'] == 'OK':
                        distance_meters = element['distance']['value']
                        distance_km = round(distance_meters / 1000.0, 2)  # Conversion en kilomètres
                        distance_matrix[i][j] = distance_km
                        distance_matrix[j][i] = distance_km  # Matrice symétrique
                    else:
                        raise ValueError(f"Impossible de calculer la distance entre {origins[i]} et {destinations[j]} : {element['status']}")

        except (ApiError, TransportError, Timeout) as e:
            raise RuntimeError(f"Erreur lors de l'appel à l'API Google Maps : {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Erreur inattendue : {str(e)}")

        return distance_matrix
        
    # def create_distance_matrix(self):
    #     coords = self.get_all_coordinates()
    #     n = len(coords)
    #     if n == 0:
    #         return [[]]
    #     distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    #     for i in range(n):
    #         for j in range(i + 1, n):
    #             coord1 = coords[i]
    #             coord2 = coords[j]
    #             if len(coord1) != 2 or len(coord2) != 2:
    #                 raise ValueError("Les coordonnées doivent être des tuples (x, y)")
    #             x1, y1 = coord1
    #             x2, y2 = coord2
    #             distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    #             distance_matrix[i][j] = distance
    #             distance_matrix[j][i] = distance
    #     return distance_matrix