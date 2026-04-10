import requests


NEO_Web = requests.get(
    "https://api.nasa.gov/neo/rest/v1/feed?start_date=2026-04-09&end_date=2026-04-23&api_key=1demxMxVcpAbySNhoLS02BuOp6aWFHBjIqbSgdtX"
)
NEO = NEO_Web.json()
print(NEO)
