import copy
import pandas as pd
import requests
import json

class Coordinates:
    def __init__(self, fichier_excel=None):
        self._coordinates_matrix = [[]]
        self._lieux = []
        self._nb_etudiant = []  # Nouvel attribut pour stocker le nombre d'étudiants
        self._api_key = 'AIzaSyA8QNEs31E8vztVT-8d3-sEAd6h6KUcyGk'

    def lire_excel(self, fichier_excel, sheet_name):
        df = pd.read_excel(fichier_excel, sheet_name=sheet_name, usecols=[0, 1, 2, 3], skiprows=2, nrows=31)  # Inclure la colonne "Nb étudiant"
        lieux = [x for x in df.iloc[:, 0].tolist() if pd.notna(x) and isinstance(x, str)]
        latitudes = [x for x in df.iloc[:, 1].tolist() if pd.notna(x) and isinstance(x, (int, float))]
        longitudes = [x for x in df.iloc[:, 2].tolist() if pd.notna(x) and isinstance(x, (int, float))]
        nb_etudiant = [int(x) if pd.notna(x) else 0 for x in df.iloc[:, 3].tolist()]  # Lire "Nb étudiant"
        min_length = min(len(lieux), len(latitudes), len(longitudes), len(nb_etudiant))
        lieux = lieux[:min_length]
        latitudes = latitudes[:min_length]
        longitudes = longitudes[:min_length]
        nb_etudiant = nb_etudiant[:min_length]
        coordinates = [(lat, lon) for lat, lon in zip(latitudes, longitudes)]
        coordinates_matrix = [[coord] for coord in coordinates]
        return lieux, coordinates_matrix, nb_etudiant  # Retourner aussi nb_etudiant

    def get_all_coordinates(self, coordinates_matrix):
        all_coordinates = []
        for row in coordinates_matrix:
            if not isinstance(row, list) or len(row) != 1 or not isinstance(row[0], tuple):
                continue
            all_coordinates.append(row[0])
        return all_coordinates
    
    def create_distance_matrix(self, fichier_excel):
        sheets = ["Coor_inst1", "Coor_inst2", "Coor_inst3"]
        all_matrices = []  # Stocker toutes les matrices pour les retourner
        for sheet in sheets:
            lieux, coordinates_matrix, nb_etudiant = self.lire_excel(fichier_excel, sheet_name=sheet)
            self._lieux = lieux
            self._nb_etudiant = nb_etudiant  # Stocker nb_etudiant
            coords = self.get_all_coordinates(coordinates_matrix)
            n = len(coords)
            if n == 0:
                print(f"Aucune coordonnée trouvée pour l'instance : {sheet}")
                continue
            distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
            
            try:
                batch_size = 25
                for start in range(0, n, batch_size):
                    end = min(start + batch_size, n)
                    origins = [{"waypoint": {"location": {"latLng": {"latitude": lat, "longitude": lon}}}} for lat, lon in coords[start:end]]
                    dest_batch_size = min(batch_size, n)
                    for dest_start in range(0, n, dest_batch_size):
                        dest_end = min(dest_start + dest_batch_size, n)
                        destinations = [{"waypoint": {"location": {"latLng": {"latitude": lat, "longitude": lon}}}} for lat, lon in coords[dest_start:dest_end]]
                        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
                        headers = {
                            "Content-Type": "application/json",
                            "X-Goog-Api-Key": self._api_key,
                            "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters"
                        }
                        payload = {
                            "origins": origins,
                            "destinations": destinations,
                            "travelMode": "DRIVE",
                            "routingPreference": "TRAFFIC_AWARE"
                        }
                        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                        if response.status_code != 200:
                            print(f"Détails de la requête pour {sheet} : {json.dumps(payload)}")
                            print(f"Détails de la réponse : {response.text}")
                            response.raise_for_status()
                        result = response.json()
                        entries = result if isinstance(result, list) else result.get("routes", [])
                        for entry in entries:
                            if isinstance(entry, dict):
                                origin_idx = entry.get("originIndex")
                                dest_idx = entry.get("destinationIndex")
                                if "distanceMeters" in entry:
                                    distance_meters = entry["distanceMeters"]
                                    distance_km = round(distance_meters / 1000.0, 2)
                                    global_i = start + origin_idx
                                    global_j = dest_start + dest_idx
                                    distance_matrix[global_i][global_j] = distance_km
                                    distance_matrix[global_j][global_i] = distance_km

            except requests.exceptions.Timeout:
                print(f"Erreur : La requête a dépassé le délai (timeout) pour {sheet}.")
            except requests.exceptions.RequestException as e:
                print(f"Attention : Échec de la Routes API pour {sheet} ({str(e)}).")
            except Exception as e:
                print(f"Erreur inattendue pour {sheet} : {str(e)}.")
            
            print(f"Matrice pour {sheet}:")
            for row in distance_matrix:
                print(row)
            all_matrices.append(distance_matrix)
        return all_matrices  # Retourner toutes les matrices

    def get_nb_etudiant(self):
        return self._nb_etudiant  # Méthode pour accéder à nb_etudiant