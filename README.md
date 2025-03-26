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
```

1. Generate an API token from Netbox web UI by clicking on the username at the top right and then API Tokens. Click on Add a Token and then on Create.
2. Copy the API token and create a .env file like the following, replacing <<API_TOKEN>> with the token:
NETBOX_URL=http://localhost:8000/api
NETBOX_TOKEN=<<API_TOKEN>>
3. Run the data initialization script with the following command:
```bash
python3 scripts/netbox_initial_data.py
```

### 4️⃣ **Run the custom script from the Netbox web UI**

1. Add the git repository to Netbox. Go to Operations > Integrations > Data Sources, click Add, select Git as Type and add the repository URL: https://github.com/miguelhormigo/netbox-task.git. Click Create.
2. Access Customization > Scripts, click Add, select the git repository as data source and then scripts/netbox_device_report.py as file. Click Create.
3. Once the script is loaded, access it by clicking the script name and run the script providing the desired parameters.

### 5️⃣ **Query device count via NetBox API**

To get the device count by status, run the following command:
```bash
python3 scripts/netbox_device_count.py
```
