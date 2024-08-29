from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
import subprocess


# Import vulnerability analyzers and ListAPIs
from vulnerabilities.Broken_Authentication import analyze_file_for_auth
from vulnerabilities.Broken_Object_Level_Authorization import analyze_file_for_bola
from vulnerabilities.SQL_Injection import analyze_file_for_sql_injection
from vulnerabilities.Unrestricted_Resource_Consumption import analyze_file_for_resource_consumption
from vulnerabilities.BOPA import analyze_file_for_broken_property_auth
from vulnerabilities.SSRF import analyze_file_for_ssrf
from vulnerabilities.BFLA import analyze_file_for_bfla
from vulnerabilities.Unrestricted_business_flow import analyze_file_for_unrestricted_business_flow
from vulnerabilities.security_misconfig import analyze_file_for_security_misconfig
from vulnerabilities.improper_inventory_management import analyze_file_for_improper_inventory_management
from vulnerabilities.unsafe_api_usage import analyze_file_for_unsafe_api_usage

from api.List_APIs import list_routes_in_file


file_path = './e-commerce.py'
app = Flask(__name__)
CORS(app)

# Global variables to cache the results
cached_api_routes = None
cached_vulnerabilities = None
last_update_time = 0
update_interval = 2  # seconds

def run_import_apis():
    """Run the import_apis.py script."""
    try:
        print("start")
        subprocess.run(["python", "import_apis.py"], check=True)
        # subprocess.run([sys.executable, "import_apis.py"], check=True)
        print("import_apis.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running import_apis.py: {e}")

def update_caches(file_path):
    global cached_api_routes, cached_vulnerabilities, last_update_time

    if time.time() - last_update_time < update_interval:
        return

    # Track if there's a change
    changes_detected = False

    # Update API routes
    new_api_routes = list_routes_in_file(file_path)
    if new_api_routes != cached_api_routes:
        cached_api_routes = new_api_routes
        with open('all_apis.txt', 'w') as api_file:
            for route in cached_api_routes:
                api_file.write(f"{route}\n")
        changes_detected = True

    # Update vulnerabilities
    new_vulnerabilities = {
        'Broken Authentication': analyze_file_for_auth(file_path),
        'Broken Object Level Authorization': analyze_file_for_bola(file_path),
        'SQL Injection': [str(v) for v in analyze_file_for_sql_injection(file_path)],
        'Unrestricted Resource Consumption': analyze_file_for_resource_consumption(file_path),
        'Broken Object Property Level Authorization': analyze_file_for_broken_property_auth(file_path),
        'SSRF': [str(v) for v in analyze_file_for_ssrf(file_path)],
        'Broken Function Level Authorization': analyze_file_for_bfla(file_path),
        'Unrestricted Business Flow': [str(v) for v in analyze_file_for_unrestricted_business_flow(file_path)],
        'Security Misconfiguration': [str(v) for v in analyze_file_for_security_misconfig(file_path)],
        'Improper Inventory Management': [str(v) for v in analyze_file_for_improper_inventory_management(file_path)],
        'Unsafe API Usage': [str(v) for v in analyze_file_for_unsafe_api_usage(file_path)]
    }

    if new_vulnerabilities != cached_vulnerabilities:
        cached_vulnerabilities = new_vulnerabilities
        with open('all_vulnerabilities.txt', 'w') as vuln_file:
            for vuln_type, vuln_list in cached_vulnerabilities.items():
                if vuln_list:
                    vuln_file.write(f"{vuln_type}:\n")
                    for vuln in vuln_list:
                        vuln_file.write(f" - {vuln}\n")
                    vuln_file.write("\n")
        changes_detected = True

    last_update_time = time.time()

    # If changes were detected, run the import_apis script
    if changes_detected:
        run_import_apis()

def run_flask():
    # Run Flask without debug mode to avoid signal issues in a secondary thread
    app.run(debug=False, host='0.0.0.0', port=5001)
    
if __name__ == '__main__':
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    while True:
        update_caches(file_path)