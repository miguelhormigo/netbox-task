# NetBox Automation Scripts

This repository contains custom scripts to automate NetBox operations, including:

- **Initializing NetBox with Sites, Racks, Device Roles, Device Types, and Devices**
- **Filtering and printing device reports in YAML format**
- **Querying device counts via the NetBox API**

These scripts are designed for use with **NetBox running on Docker (WSL)** and can be executed via the Web UI or CLI.

---

## 🚀 Installation & Setup

### 1️⃣ Install & Start NetBox with Docker

Clone the NetBox Docker repository and start the containerized NetBox instance:

```bash
Copy
Edit
git clone -b release https://github.com/netbox-community/netbox-docker.git
cd netbox-docker
tee docker-compose.override.yml <<EOF
services:
  netbox:
    ports:
      - 8000:8080
EOF
docker compose pull
docker compose up
```

The whole application will be available after a few minutes.
Open the URL `http://0.0.0.0:8000/` in a web-browser.
You should see the NetBox homepage.

To create the first admin user run this command:

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
```

### 2️⃣ **Find SWL IP address and access Netbox**

Run the following command inside WSL to find your local IP address:

```bash
ip addr show eth0 | grep "inet"
```

Enter http://<WSL-IP>:8000/ in a browser, replacing <WSL-IP> with the actual IP address.

### 3️⃣ **Clone this repository and run script to initialize with the predefined data**

```bash
git clone https://github.com/miguelhormigo/netbox-task.git
cd netbox-task
pip install -r requirements.txt
python3 scripts/netbox_initial_data.py
```
