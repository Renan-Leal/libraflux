import os
from nest.core import Injectable
import requests

# TODO: Implement a more robust health check mechanism (db connection and memory usage)


@Injectable
class HealthService:
    def __init__(self):
        self.base_url = os.environ.get("URL_TO_SCRAPE")

    def check(self):
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                return {"status": "up", "message": "API is up and running"}
            else:
                return {
                    "status": "down",
                    "message": f"API returned status code {response.status_code}",
                }
        except Exception as e:
            return {"status": "down", "message": f"Error: {str(e)}"}
