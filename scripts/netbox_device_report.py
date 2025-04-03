import yaml
from dcim.models import Device, Site, Rack
from extras.scripts import *
# from fpdf import FPDF

class DeviceReport(Script):
    """Generates a YAML report of devices filtered by Site, Rack, and Status"""

    class Meta:
        name = "Device Report"
        description = "Generates a YAML report of devices filtered by Site, Rack, and Status"
        field_order = ['status', 'site', 'rack', 'save_pdf']

    status = ChoiceVar(
        choices=[("active", "Active"), ("planned", "Planned"), ("decommissioned", "Decommissioned")],
        label="Device Status",
        required=True
    )
    site = ObjectVar(
        model=Site,
        required=False,
        label="Filter by Site"
    )
    rack = ObjectVar(
        model=Rack,
        required=False,
        label="Filter by Rack"
    )
    # TODO: uncomment once fpdf import problem is solved
    # save_pdf = BooleanVar(
    #     label="Save report as PDF?",
    #     default=False
    # )

    def run(self, data, commit):
        """Fetch and process devices based on filters"""
        try:
            # Validate that at least one optional filter is selected
            if not data["site"] and not data["rack"]:
                self.log_failure("❌ At least one additional filter (Site or Rack) must be selected.")
                return "Error: At least one additional filter (Site or Rack) must be selected."

            devices = Device.objects.filter(status=data["status"])

            if data["site"]:
                devices = devices.filter(site=data["site"])
            if data["rack"]:
                devices = devices.filter(rack=data["rack"])

            if not devices.exists():
                self.log_warning("⚠️ No devices found matching the filters.", type(devices))
                return "No devices found."

            # Structure data for YAML output
            structured_data = {}

            for device in devices:
                site_name = device.site.name if device.site else "Unknown"
                rack_name = device.rack.name if device.rack else "No Rack"

                # Ensure site exists in dict
                if site_name not in structured_data:
                    structured_data[site_name] = {}

                # Ensure rack exists in site
                if rack_name not in structured_data[site_name]:
                    structured_data[site_name][rack_name] = []
                
                structured_data[site_name][rack_name].append(device.name)

            # Convert to YAML
            yaml_output = yaml.dump(structured_data, default_flow_style=False, allow_unicode=True)
            self.log_success("✅ YAML report generated successfully.")
            self.log_info(yaml_output)

            # # Save as PDF (optional)
            # if data["save_pdf"]:
            #     self.save_to_pdf(yaml_output)

            return yaml_output

        except Exception as e:
            error_msg = f"❌ Error generating device report: {str(e)}"
            self.log_failure(error_msg)

    # def save_to_pdf(self, yaml_data, filename="/opt/netbox/netbox/media/netbox_devices.pdf"):
    #     """Save YAML output to a PDF file"""
    #     try:
    #         pdf = FPDF()
    #         pdf.set_auto_page_break(auto=True, margin=10)
    #         pdf.add_page()
    #         pdf.set_font("Courier", size=10)

    #         for line in yaml_data.split("\n"):
    #             pdf.cell(200, 6, line, ln=True)

    #         pdf.output(filename)
    #         self.log_success(f"📄 PDF saved as {filename}")

    #     except Exception as e:
    #         error_msg = f"❌ Failed to save PDF: {str(e)}"
    #         self.log_failure(error_msg)
