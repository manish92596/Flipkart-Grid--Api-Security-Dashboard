from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import threading
import time

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Establish and return a MySQL database connection."""
    return mysql.connector.connect(
        host="api-security-db.co0ynpevyflj.ap-south-1.rds.amazonaws.com",
        user="root",
        password="abhi1301",
        database="api_database",
        port=5506
    )

# Existing routes
@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Fetch API routes from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT path, methods FROM api_routes")
    routes = cursor.fetchall()
    
    for route in routes:
        route['methods'] = route['methods'].split(', ')
    
    cursor.close()
    conn.close()
    return jsonify(routes)

@app.route('/api/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    """Fetch vulnerabilities from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT vulnerability_type, route_name FROM vulnerabilities")
    vulnerabilities = cursor.fetchall()
    cursor.close()
    conn.close()

    grouped_vulnerabilities = {}
    for vuln in vulnerabilities:
        vuln_type = vuln['vulnerability_type']
        if vuln_type not in grouped_vulnerabilities:
            grouped_vulnerabilities[vuln_type] = []
        grouped_vulnerabilities[vuln_type].append(vuln['route_name'])

    return jsonify(grouped_vulnerabilities)

@app.route('/api/vulnerabilities/<path:path>', methods=['GET'])
def get_vulnerability_details(path):
    """Fetch vulnerabilities for a specific API route from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT vulnerability_type FROM vulnerabilities WHERE route_name = %s", (path,))
    vulnerabilities = cursor.fetchall()
    cursor.close()
    conn.close()

    route_vulnerabilities = {vuln['vulnerability_type']: path for vuln in vulnerabilities}
    return jsonify(route_vulnerabilities)

# New routes
@app.route('/api/total_apis', methods=['GET'])
def get_total_apis():
    """Fetch total number of APIs from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM api_routes")
    total_apis = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify(total_apis)

@app.route('/api/total_vulnerabilities', methods=['GET'])
def get_total_vulnerabilities():
    """Fetch total number of vulnerabilities from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
    total_vulnerabilities = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify(total_vulnerabilities)

@app.route('/api/vulnerabilities/severity', methods=['GET'])
def get_vulnerabilities_severity():
    """Fetch severity of vulnerabilities from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT vulnerability_type, severity_score as count FROM vulnerability_severity
    """)
    severity_data = cursor.fetchall()
    cursor.close()
    conn.close()

    severity_map = {
        'Critical': 4,
        'High': 3,
        'Medium': 2,
        'Low': 1
    }

    severity = {}
    for item in severity_data:
        vulnerability = item['vulnerability_type']
        count = item['count']
        severity_level = severity_map.get(vulnerability, 1)
        severity[vulnerability] = severity_level * count

    return jsonify(severity)

@app.route('/api/vulnerabilities/timeline', methods=['GET'])
def get_vulnerabilities_timeline():
    """Fetch the latest 15 entries of vulnerabilities from the live_graph table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, vulnerabilities FROM live_graph ORDER BY id DESC LIMIT 15")
    timeline_data = cursor.fetchall()
    timeline_data.reverse()  # Reverse to maintain chronological order
    cursor.close()
    conn.close()
    return jsonify(timeline_data)

@app.route('/api/code_score', methods=['GET'])
def get_code_score():
    """Fetch a calculated score of code quality from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
    total_vulnerabilities = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    # Simple logic to calculate code score
    code_score = max(0, 100 - total_vulnerabilities * 2)  # For instance, 2 points per vulnerability
    return jsonify(code_score)

# Function to insert vulnerability count into live_graph table
def insert_vulnerability_count():
    """Periodically insert the total number of vulnerabilities into the live_graph table."""
    while True:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
        total_vulnerabilities = cursor.fetchone()[0]
        print(total_vulnerabilities)

        cursor.execute("INSERT INTO live_graph (vulnerabilities) VALUES (%s)", (total_vulnerabilities,))
        conn.commit()
        cursor.close()
        conn.close()

        time.sleep(5)

# Run the Flask app
if __name__ == '__main__':
    # Start the thread to insert vulnerability count into live_graph periodically
    threading.Thread(target=insert_vulnerability_count, daemon=True).start()

    app.run(debug=True, host='0.0.0.0', port=5001)  # Set debug to False in a production environment
