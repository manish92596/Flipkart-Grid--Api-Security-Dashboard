from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

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

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Fetch API routes from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT path, methods FROM api_routes")
    routes = cursor.fetchall()
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

    # Group vulnerabilities by type
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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)  # Set debug to False in a production environment
