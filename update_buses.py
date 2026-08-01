import requests
import json
from datetime import datetime, timezone
from google.transit import gtfs_realtime_pb2

URL = "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position"


def nom_ligne(route_id):

    if route_id == "0100":
        return "La Navette"

    if route_id == "0803":
        return "API"

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

    return route_id[-2:]


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

        code_ligne = vehicle.trip.route_id

        properties["route_id"] = code_ligne
        properties["ligne"] = nom_ligne(code_ligne)

        properties["trip_id"] = vehicle.trip.trip_id
        properties["direction_id"] = vehicle.trip.direction_id

    if vehicle.current_stop_sequence:
        properties["stop_sequence"] = vehicle.current_stop_sequence

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

    json.dump(
        geojson,
        f,
        ensure_ascii=False
    )

from datetime import datetime, timezone

print(f"{len(features)} bus enregistrés")
print("Mise à jour effectuée :", datetime.now(timezone.utc).isoformat())
