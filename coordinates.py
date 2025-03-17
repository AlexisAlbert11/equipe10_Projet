import copy
import pandas as pd
import requests

class Coordinates:
    def __init__(self, coordinates_matrix=[[]], lieux=None, fichier_excel=None, sheet_name=0):
        if fichier_excel:
            lieux, coordinates_matrix = self.lire_excel(fichier_excel, sheet_name)
        self._coordinates_matrix = copy.deepcopy(coordinates_matrix)
        self._lieux = lieux if lieux else [f"Lieu {i+1}" for i in range(len(coordinates_matrix))]
        self._api_key = 'AIzaSyBO9Z54wXRhMwm-KdVh7tyLebe8_5SXO7w'

    def lire_excel(self, fichier_excel, sheet_name):
        df = pd.read_excel(fichier_excel, sheet_name=sheet_name, usecols=[2, 3, 4], skiprows=1, nrows=31)
        lieux = [x for x in df.iloc[:, 0].tolist() if pd.notna(x)]
        latitudes = [x for x in df.iloc[:, 1].tolist() if pd.notna(x)]
        longitudes = [x for x in df.iloc[:, 2].tolist() if pd.notna(x)]
        coordinates = [(lat, lon) for lat, lon in zip(latitudes, longitudes) if pd.notna(lat) and pd.notna(lon)]
        coordinates_matrix = [[coord] for coord in coordinates]
        return lieux, coordinates_matrix

    def __str__(self):
        if not self._coordinates_matrix or all(not row for row in self._coordinates_matrix):
            return "Matrice de coordonnées vide"
        n_rows = len(self._coordinates_matrix)
        if len(self._lieux) != n_rows:
            return "Erreur : Le nombre de noms de lieux ne correspond pas au nombre de lignes"
        for row in self._coordinates_matrix:
            if not row or not isinstance(row, list) or len(row) != 1 or not isinstance(row[0], tuple):
                return "Erreur : Chaque ligne doit contenir exactement un tuple de coordonnées"
        lieu_noms = self._lieux
        max_width = max(len(str(row[0])) for row in self._coordinates_matrix) + 2
        max_label_width = max(len(label) for label in lieu_noms) + 2
        lignes = [" " * max_label_width + "Coordonnées"]
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
        coords = self.get_all_coordinates()
        n = len(coords)
        if n == 0:
            return [[]]
        print(f"Calcul des distances pour {n} lieux ({n*n} paires)...")
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        try:
            print("Préparation des données pour la requête API...")
            batch_size = 25
            for start in range(0, n, batch_size):
                end = min(start + batch_size, n)
                origins_batch = [f"{lat},{lon}" for lat, lon in coords[start:end]]
                for dest_start in range(0, n, batch_size):
                    dest_end = min(dest_start + batch_size, n)
                    destinations_batch = [f"{lat},{lon}" for lat, lon in coords[dest_start:dest_end]]
                    print(f"Traitement du bloc {start}-{end} vers {dest_start}-{dest_end}...")
                    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
                    params = {
                        "origins": "|".join(origins_batch),
                        "destinations": "|".join(destinations_batch),
                        "mode": "driving",
                        "key": self._api_key
                    }
                    print("Envoi de la requête à l'API Distance Matrix...")
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    print("Réponse reçue. Traitement des données...")
                    if result["status"] != "OK":
                        print("Détails de la réponse :", result)
                        raise ValueError(f"Erreur de l'API Distance Matrix : {result.get('status')}")
                    for i, row in enumerate(result["rows"]):
                        for j, element in enumerate(row["elements"]):
                            if element["status"] == "OK":
                                distance_meters = element["distance"]["value"]
                                distance_km = round(distance_meters / 1000.0, 2)
                                global_i = start + i
                                global_j = dest_start + j
                                distance_matrix[global_i][global_j] = distance_km
                                distance_matrix[global_j][global_i] = distance_km
                                print(f"Distance entre {global_i} et {global_j} : {distance_km} km")
                            else:
                                print(f"Pas de distance entre {start+i} et {dest_start+j} : {element['status']}")
        except requests.exceptions.Timeout:
            print("Erreur : La requête a dépassé le délai (timeout). Utilisation d'une matrice par défaut.")
        except requests.exceptions.RequestException as e:
            print(f"Attention : Échec de l'API Distance Matrix ({str(e)}). Utilisation d'une matrice par défaut de 0.")
        except Exception as e:
            print(f"Erreur inattendue : {str(e)}. Utilisation d'une matrice par défaut de 0.")
        print("Matrice de distances calculée.")
        return distance_matrix