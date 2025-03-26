import requests
import os
import argparse
import json
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

NETBOX_URL = os.getenv("NETBOX_URL", "http://localhost:8000/api")
TOKEN = os.getenv("NETBOX_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

def get_device_count(status=None):
    """Fetches the number of devices from NetBox, optionally filtered by status"""
    url = f"{NETBOX_URL}/dcim/devices/"
    params = {}

    if status:
        params["status"] = status

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        devices = response.json().get("results", [])

        if status:
            print(f"✅ Total devices with status '{status}': {len(devices)}")
        else:
            # Count devices by status
            status_counts = {}
            for device in devices:
                print(device["status"])
                device_status = device["status"]["value"] if device.get("status") else "unknown"
                status_counts[device_status] = status_counts.get(device_status, 0) + 1
            
            print("📊 Device count by status:")
            print(json.dumps(status_counts, indent=2))

        return len(devices) if status else status_counts

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to NetBox: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query NetBox API for device count")
    parser.add_argument("--status", type=str, help="Filter devices by status (e.g., 'active', 'planned', 'decommissioned')")
    
    args = parser.parse_args()
    
    get_device_count(args.status)
