
import requests
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the URL of the Flask endpoint
url = "http://127.0.0.1:5001/scan"

# Define the data to send in the POST request
data = {
    "db_host": "localhost",
    "db_user": "root",
    "db_password": "manish302",
    "db_name": "api_database",
    "db_port": 3306
}

# The file path to monitor
file_path = "e-commerce.py"

def scan_file():
    """Send an initial scan request for the file."""
    print(f"Scanning {file_path}...")
    updated_data = {**data, "file_path": file_path}
    response = requests.post(url, json=updated_data)
    print("Initial Scan - Status Code:", response.status_code)
    print("Response Text:", response.text)

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(os.path.basename(file_path)):
            print(f"{event.src_path} has been modified, sending request...")
            updated_data = {**data, "file_path": file_path}
            response = requests.post(url, json=updated_data)
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

def monitor_file():
    # Perform an initial scan once
    scan_file()

    # Monitor the file for changes
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(file_path)), recursive=False)
    observer.start()
    print(f"Started monitoring {file_path} for changes...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    monitor_file()
