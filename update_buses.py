```yaml
name: Mise à jour des bus STAR

on:
  schedule:
    - cron: "*/5 * * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Installer Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Installer les dépendances
        run: pip install -r requirements.txt

      - name: Récupérer les positions STAR
        run: python update_buses.py

      - name: Publier le GeoJSON
        run: |
          git config user.name "STAR Bus Tracker"
          git config user.email "actions@github.com"

          git add bus.geojson

          git diff --cached --quiet || git commit -m "Mise à jour des positions"

          git pull --rebase origin main

          git push
```
