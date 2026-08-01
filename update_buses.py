import requests
import json
from google.transit import gtfs_realtime_pb2

URL = "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position"

response = requests.get(URL, timeout=30)
response.raise_for_status()

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

features = []

for entity in feed.entity:
    if not entity.HasField("vehicle"):
        continue

    vehicle = entity.vehicle

    if not vehicle.position.latitude or not vehicle.position.longitude:
        continue

    properties = {}

    if vehicle.vehicle:
        properties["vehicle_id"] = vehicle.vehicle.id
        properties["vehicle_label"] = vehicle.vehicle.label

    if vehicle.trip:
        properties["trip_id"] = vehicle.trip.trip_id
        properties["route_id"] = vehicle.trip.route_id
        properties["direction_id"] = vehicle.trip.direction_id

    if vehicle.current_stop_sequence:
        properties["stop_sequence"] = vehicle.current_stop_sequence

    if vehicle.current_status:
        properties["current_status"] = vehicle.current_status

    if vehicle.timestamp:
        properties["timestamp"] = vehicle.timestamp

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

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open("bus.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False)

print(f"{len(features)} bus enregistrés")
```python
# ============================================================
# CORRESPONDANCE ID LIGNE STAR → NOM DE LIGNE
# ============================================================

def nom_ligne(route_id):

    # --------------------------------------------------------
    # CAS PARTICULIERS
    # --------------------------------------------------------

    # La Navette
    if route_id == "0100":
        return "La Navette"

    # API
    if route_id == "0803":
        return "API"


    # --------------------------------------------------------
    # LIGNES CHRONOSTAR C1 À C7
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # TOUTES LES AUTRES LIGNES
    # On garde uniquement les deux derniers chiffres
    # --------------------------------------------------------

    return route_id[-2:]
```
