from flask import Flask, Response
import requests
from google.transit import gtfs_realtime_pb2
import json
from datetime import datetime, timezone

app = Flask(__name__)

STAR_URL = "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position"


@app.route("/")
def accueil():
    return "GeoBus Rennes fonctionne ! 🚌"


@app.route("/bus.geojson")
def bus_geojson():

    # Récupération du flux temps réel STAR
    response = requests.get(STAR_URL, timeout=15)
    response.raise_for_status()

    # Lecture du GTFS-RT
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    features = []

    for entity in feed.entity:

        if not entity.HasField("vehicle"):
            continue

        vehicle = entity.vehicle

        if not vehicle.position:
            continue

        latitude = vehicle.position.latitude
        longitude = vehicle.position.longitude

        properties = {}

        if vehicle.vehicle:
            properties["vehicle_id"] = vehicle.vehicle.id
            properties["vehicle_label"] = vehicle.vehicle.label

        if vehicle.trip:
            properties["trip_id"] = vehicle.trip.trip_id
            properties["route_id"] = vehicle.trip.route_id

        properties["last_update"] = datetime.now(
            timezone.utc
        ).isoformat()

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    longitude,
                    latitude
                ]
            },
            "properties": properties
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return Response(
        json.dumps(geojson, ensure_ascii=False),
        mimetype="application/geo+json"
    )


if __name__ == "__main__":
    app.run()
