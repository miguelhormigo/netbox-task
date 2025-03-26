import requests
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load environment variables from .env
load_dotenv()

NETBOX_URL = os.getenv("NETBOX_URL", "http://localhost:8000/api")
TOKEN = os.getenv("NETBOX_TOKEN")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Helper function to create an object in NetBox
def create_object(endpoint, data, keyname='name'):
    response = requests.post(f"{NETBOX_URL}/{endpoint}/", headers=HEADERS, json=data)
    response_data = response.json()
    
    if response.status_code == 201:
        logging.info(f"✅ Created {endpoint[:-1]}: {data[keyname]}")
        return response_data.get("id")
    else:
        logging.error(f"❌ Error creating {endpoint[:-1]}: {response_data}")
        exit(1)

# Ensure API connectivity
try:
    test_response = requests.get(f"{NETBOX_URL}/dcim/sites/", headers=HEADERS)
    test_response.raise_for_status()
    logging.info("✅ NetBox API is reachable.")
except requests.RequestException as e:
    logging.error(f"❌ Failed to connect to NetBox: {e}")
    exit(1)

# Step 1: Create Manufacturer
manufacturer_data = {"name": "Cisco", "slug": "cisco"}
manufacturer_id = create_object("dcim/manufacturers", manufacturer_data)

# Step 2: Create Device Types
device_types = {}
for device in ["Switch", "Router", "Firewall"]:
    device_type_data = {
        "manufacturer": manufacturer_id,
        "model": f"Cisco {device} Model",
        "slug": f"cisco-{device.lower()}",
    }
    device_types[device] = create_object("dcim/device-types", device_type_data, keyname='model')

# Step 3: Create Device Roles
device_roles = {}
for role in ["Switch", "Router", "Firewall"]:
    device_role_data = {"name": role, "slug": role.lower(), "color": "ff0000"}
    device_roles[role] = create_object("dcim/device-roles", device_role_data)

# Step 4: Create Sites
site_ids = {}
for i in range(1, 3):
    site_data = {"name": f"Site {i}", "slug": f"site-{i}"}
    site_ids[i] = create_object("dcim/sites", site_data)

# Step 5: Create Racks (2 per Site)
rack_ids = []
rack_count = 1
for site_id in site_ids.values():
    for _ in range(2):
        rack_data = {"name": f"Rack {rack_count}", "site": site_id}
        rack_ids.append(create_object("dcim/racks", rack_data))
        rack_count += 1

# Step 6: Create Devices (10 per Site, assign to 1st rack per site)
for i, site_id in site_ids.items():
    rack_id = rack_ids[(i - 1) * 2]  # First rack of the site
    for j in range(1, 11):
        role = list(device_roles.keys())[j % len(device_roles)]
        device_data = {
            "name": f"Device {j} - Site {i}",
            "site": site_id,
            "rack": rack_id,
            "status": "active",  # Valid status
            "role": device_roles[role],  # Use correct field name
            "device_type": device_types[role]  # Use correct field name
        }
        create_object("dcim/devices", device_data)

logging.info("✅ Data successfully added to NetBox")
