# from flask import Flask, jsonify
# from flask_cors import CORS
# import threading
# import time
# import subprocess


# # Import vulnerability analyzers and ListAPIs
# from vulnerabilities.Broken_Authentication import analyze_file_for_auth
# from vulnerabilities.Broken_Object_Level_Authorization import analyze_file_for_bola
# from vulnerabilities.SQL_Injection import analyze_file_for_sql_injection
# from vulnerabilities.Unrestricted_Resource_Consumption import analyze_file_for_resource_consumption
# from vulnerabilities.BOPA import analyze_file_for_broken_property_auth
# from vulnerabilities.SSRF import analyze_file_for_ssrf
# from vulnerabilities.BFLA import analyze_file_for_bfla
# from vulnerabilities.Unrestricted_business_flow import analyze_file_for_unrestricted_business_flow
# from vulnerabilities.security_misconfig import analyze_file_for_security_misconfig
# from vulnerabilities.improper_inventory_management import analyze_file_for_improper_inventory_management
# from vulnerabilities.unsafe_api_usage import analyze_file_for_unsafe_api_usage

# from api.List_APIs import list_routes_in_file


# file_path = './e-commerce.py'
# app = Flask(__name__)
# CORS(app)

# # Global variables to cache the results
# cached_api_routes = None
# cached_vulnerabilities = None
# last_update_time = 0
# update_interval = 2  # seconds

# def run_import_apis():
#     """Run the import_apis.py script."""
#     try:
#         print("start")
#         subprocess.run(["python", "import_apis.py"], check=True)
#         # subprocess.run([sys.executable, "import_apis.py"], check=True)
#         print("import_apis.py executed successfully.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error running import_apis.py: {e}")

# def update_caches(file_path):
#     global cached_api_routes, cached_vulnerabilities, last_update_time

#     if time.time() - last_update_time < update_interval:
#         return

#     # Track if there's a change
#     changes_detected = False

#     # Update API routes
#     new_api_routes = list_routes_in_file(file_path)
#     if new_api_routes != cached_api_routes:
#         cached_api_routes = new_api_routes
#         with open('all_apis.txt', 'w') as api_file:
#             for route in cached_api_routes:
#                 api_file.write(f"{route}\n")
#         changes_detected = True

#     # Update vulnerabilities
#     new_vulnerabilities = {
#         'Broken Authentication': analyze_file_for_auth(file_path),
#         'Broken Object Level Authorization': analyze_file_for_bola(file_path),
#         'SQL Injection': [str(v) for v in analyze_file_for_sql_injection(file_path)],
#         'Unrestricted Resource Consumption': analyze_file_for_resource_consumption(file_path),
#         'Broken Object Property Level Authorization': analyze_file_for_broken_property_auth(file_path),
#         'SSRF': [str(v) for v in analyze_file_for_ssrf(file_path)],
#         'Broken Function Level Authorization': analyze_file_for_bfla(file_path),
#         'Unrestricted Business Flow': [str(v) for v in analyze_file_for_unrestricted_business_flow(file_path)],
#         'Security Misconfiguration': [str(v) for v in analyze_file_for_security_misconfig(file_path)],
#         'Improper Inventory Management': [str(v) for v in analyze_file_for_improper_inventory_management(file_path)],
#         'Unsafe API Usage': [str(v) for v in analyze_file_for_unsafe_api_usage(file_path)]
#     }

#     if new_vulnerabilities != cached_vulnerabilities:
#         cached_vulnerabilities = new_vulnerabilities
#         with open('all_vulnerabilities.txt', 'w') as vuln_file:
#             for vuln_type, vuln_list in cached_vulnerabilities.items():
#                 if vuln_list:
#                     vuln_file.write(f"{vuln_type}:\n")
#                     for vuln in vuln_list:
#                         vuln_file.write(f" - {vuln}\n")
#                     vuln_file.write("\n")
#         changes_detected = True

#     last_update_time = time.time()

#     # If changes were detected, run the import_apis script
#     if changes_detected:
#         run_import_apis()

# def run_flask():
#     # Run Flask without debug mode to avoid signal issues in a secondary thread
#     app.run(debug=False, host='0.0.0.0', port=5001)
    
# if __name__ == '__main__':
#     # Start Flask server in a separate thread
#     flask_thread = threading.Thread(target=run_flask)
#     flask_thread.start()
#     while True:
#         update_caches(file_path)



# new code with script optimize 
import subprocess
import logging
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

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

# Setup logging to save logs in events_log.txt
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("events_log.txt"),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

# Global variables to cache the results
cached_api_routes = None
cached_vulnerabilities = None

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, debounce_time=1.0):
        self.file_path = os.path.abspath(file_path)
        self.debounce_time = debounce_time
        self.last_modified = time.time()

    def on_modified(self, event):
        # Ensure that we're comparing absolute paths
        event_path = os.path.abspath(event.src_path)

        if event_path == self.file_path:
            now = time.time()
            if now - self.last_modified >= self.debounce_time:
                self.last_modified = now
                logger.info(f"Detected change in {self.file_path}. Updating caches...")
                update_caches(self.file_path)
            else:
                logger.debug(f"Change detected, but within debounce period. Ignoring.")

def run_import_apis():
    """Run the import_apis.py script."""
    try:
        logger.info("Running import_apis.py...")
        subprocess.run(["python", "import_apis.py"], check=True)
        logger.info("import_apis.py executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running import_apis.py: {e}")

def update_caches(file_path):
    global cached_api_routes, cached_vulnerabilities

    # Track if there's a change
    changes_detected = False

    # Update API routes
    logger.debug("Search API routes...")
    new_api_routes = list_routes_in_file(file_path)
    if new_api_routes != cached_api_routes:
        cached_api_routes = new_api_routes
        with open('all_apis.txt', 'w') as api_file:
            for route in cached_api_routes:
                api_file.write(f"{route}\n")
        logger.info(f"API routes updated: {new_api_routes}")
        changes_detected = True

    # Update vulnerabilities
    logger.debug("Found vulnerabilities...")
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
        logger.info(f"Vulnerabilities updated: {new_vulnerabilities}")
        changes_detected = True

    # If changes were detected, run the import_apis script
    if changes_detected:
        run_import_apis()

def monitor_file(file_path):
    print("4")
    event_handler = FileChangeHandler(file_path)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(file_path)), recursive=False)
    observer.start()
    logger.info(f"Started monitoring {file_path} for changes...")
    print("5")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    # Parse the command-line arguments to get the file path
    parser = argparse.ArgumentParser(description='Run the API scanner.')
    parser.add_argument('--file_path', type=str, required=True, help='Path to the file to be scanned (e.g., e-commerce.py)')
    args = parser.parse_args()
    print("1")

    file_path = args.file_path  # Use the file path provided by the user

    # Ensure the file exists before monitoring
    if not os.path.exists(file_path):
        logger.error(f"The file {file_path} does not exist. Exiting...")
        exit(1)
    print("2")
    # Monitor the file for changes and update caches accordingly
    monitor_file(file_path)
    print("3")
