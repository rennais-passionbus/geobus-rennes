```python
import requests
import json
from google.transit import gtfs_realtime_pb2


# ============================================================
# URL DU FLUX TEMPS RÉEL STAR
# ============================================================

URL = "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position"


# ============================================================
# CORRESPONDANCE ID LIGNE STAR → NOM DE LIGNE
# ============================================================

def nom_ligne(route_id):

    # Lignes particulières
    if route_id == "0100":
        return "La Navette"

    if route_id == "0803":
        return "API"

    # Chronostar C1 à C7
    if route_id == "0001":
        return "C1"

    if route_id == "0002":
        return "C2"

    if route_id == "0003":
        return "C3"

    if route_id == "0004":
        return "C4"

    if route_id == "0005":
        return "C5"

    if route_id == "0006":
        return "C6"

    if route_id == "0007":
        return "C7"

    # Toutes les autres lignes :
    # on conserve les deux derniers chiffres
    return route_id[-2:]


# ============================================================
# RÉCUPÉRATION DES DONNÉES STAR
# ============================================================

response = requests.get(URL, timeout=30)
response.raise_for_status()

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)


# ============================================================
# CRÉATION DU GEOJSON
# ============================================================

features = []


for entity in feed.entity:

    if not entity.HasField("vehicle"):
        continue

    vehicle = entity.vehicle

    # Ignorer les véhicules sans position
    if not vehicle.position.latitude or not vehicle.position.longitude:
        continue

    properties = {}


    # ========================================================
    # INFORMATIONS DU VÉHICULE
    # ========================================================

    if vehicle.vehicle:
        properties["vehicle_id"] = vehicle.vehicle.id
        properties["vehicle_label"] = vehicle.vehicle.label


    # ========================================================
    # INFORMATIONS DE LA LIGNE
    # ========================================================

    if vehicle.trip:

        code_ligne = vehicle.trip.route_id

        # ID technique STAR
        properties["route_id"] = code_ligne

        # Nom lisible de la ligne
        properties["ligne"] = nom_ligne(code_ligne)

        # Autres informations
        properties["trip_id"] = vehicle.trip.trip_id
        properties["direction_id"] = vehicle.trip.direction_id


    # ========================================================
    # AUTRES INFORMATIONS
    # ========================================================

    if vehicle.current_stop_sequence:
        properties["stop_sequence"] = vehicle.current_stop_sequence

    if vehicle.current_status:
        properties["current_status"] = vehicle.current_status

    if vehicle.timestamp:
        properties["timestamp"] = vehicle.timestamp


    # ========================================================
    # CRÉATION DU POINT GEOJSON
    # ========================================================

    feature = {
        "type": "Feature",

        "geometry": {
            "type": "Point",
            "coordinates": [
                vehicle.position.longitude,
                vehicle.position.latitude
            ]
        },

        "properties": properties
    }

    features.append(feature)


# ============================================================
# CRÉATION DU FICHIER FINAL
# ============================================================

geojson = {
    "type": "FeatureCollection",
    "features": features
}


with open("bus.geojson", "w", encoding="utf-8") as f:
    json.dump(
        geojson,
        f,
        ensure_ascii=False
    )


print(f"{len(features)} bus enregistrés")
```
