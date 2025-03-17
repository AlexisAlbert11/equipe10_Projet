import copy
import pandas as pd
import requests
import json

class Coordinates:
    def __init__(self, coordinates_matrix=[[]], lieux=None, fichier_excel=None, sheet_name=0):
        if fichier_excel:
            lieux, coordinates_matrix = self.lire_excel(fichier_excel, sheet_name)
        self._coordinates_matrix = copy.deepcopy(coordinates_matrix)
        self._lieux = lieux if lieux else [f"Lieu {i+1}" for i in range(len(coordinates_matrix))]
        self._api_key = 'AIzaSyA8QNEs31E8vztVT-8d3-sEAd6h6KUcyGk'  # Utilisez votre clé API

    def lire_excel(self, fichier_excel, sheet_name):
        df = pd.read_excel(fichier_excel, sheet_name=sheet_name, usecols=[2, 3, 4], skiprows=2, nrows=32)  # Lire de la ligne 3 à 34
        lieux = [x for x in df.iloc[:, 0].tolist() if pd.notna(x) and isinstance(x, str)]
        latitudes = [x for x in df.iloc[:, 1].tolist() if pd.notna(x) and isinstance(x, (int, float))]
        longitudes = [x for x in df.iloc[:, 2].tolist() if pd.notna(x) and isinstance(x, (int, float))]
        # Vérifier que les listes ont la même longueur
        min_length = min(len(lieux), len(latitudes), len(longitudes))
        lieux = lieux[:min_length]
        latitudes = latitudes[:min_length]
        longitudes = longitudes[:min_length]
        coordinates = [(lat, lon) for lat, lon in zip(latitudes, longitudes)]
        coordinates_matrix = [[coord] for coord in coordinates]
        print(f"Lieux lus : {lieux}")  # Débogage pour vérifier les lieux
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
            batch_size = 25  # Limite pour rester sous 625 éléments (25 x 25 = 625)
            for start in range(0, n, batch_size):
                end = min(start + batch_size, n)
                origins = [{"waypoint": {"location": {"latLng": {"latitude": lat, "longitude": lon}}}} for lat, lon in coords[start:end]]
                # Limiter les destinations au même batch_size pour respecter 625
                dest_batch_size = min(batch_size, n)
                for dest_start in range(0, n, dest_batch_size):
                    dest_end = min(dest_start + dest_batch_size, n)
                    destinations = [{"waypoint": {"location": {"latLng": {"latitude": lat, "longitude": lon}}}} for lat, lon in coords[dest_start:dest_end]]
                    
                    print(f"Traitement du bloc {start}-{end} (origines) vers {dest_start}-{dest_end} (destinations)...")
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
                    
                    print("Envoi de la requête à la Routes API...")
                    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                    if response.status_code != 200:
                        print(f"Détails de la requête : {json.dumps(payload)}")  # Débogage
                        print(f"Détails de la réponse : {response.text}")
                        response.raise_for_status()
                    result = response.json()
                    
                    print("Réponse reçue. Traitement des données...")
                    # Vérifier si result est une liste directement
                    entries = result if isinstance(result, list) else result.get("routes", [])
                    for entry in entries:
                        if isinstance(entry, dict):  # Vérifier que c'est un dictionnaire
                            origin_idx = entry.get("originIndex")
                            dest_idx = entry.get("destinationIndex")
                            if "distanceMeters" in entry:
                                distance_meters = entry["distanceMeters"]
                                distance_km = round(distance_meters / 1000.0, 2)
                                global_i = start + origin_idx
                                global_j = dest_start + dest_idx
                                distance_matrix[global_i][global_j] = distance_km
                                distance_matrix[global_j][global_i] = distance_km  # Symétrique pour driving
                                print(f"Distance entre {global_i} et {global_j} : {distance_km} km")
                            else:
                                print(f"Pas de distance entre {start+origin_idx} et {dest_start+dest_idx} : {entry.get('status', 'N/A')}")

        except requests.exceptions.Timeout:
            print("Erreur : La requête a dépassé le délai (timeout). Utilisation d'une matrice par défaut.")
        except requests.exceptions.RequestException as e:
            print(f"Attention : Échec de la Routes API ({str(e)}). Utilisation d'une matrice par défaut de 0.")
        except Exception as e:
            print(f"Erreur inattendue : {str(e)}. Utilisation d'une matrice par défaut de 0.")
        
        print("Matrice de distances calculée.")
        return distance_matrix