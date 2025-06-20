from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route('/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user_id = data.get('id')
    role = data.get('role')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_auth WHERE user_id = %s AND role = %s", (user_id, role))
        user = cursor.fetchone()

        if user and user['password'] == password:
            return jsonify({"success": True, "user": {"id": user['user_id'], "role": user['role']}})
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/grievances', methods=['GET'])
def get_grievances():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM grievances")
        grievances = cursor.fetchall()
        return jsonify(grievances)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/grievances', methods=['POST'])
def create_grievance():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO grievances (student_id, student_name, student_usn, type, description, priority, status, submission_date, last_updated, current_handler, handler_role)
            VALUES (%s, %s, %s, %s, %s, %s, 'submitted', NOW(), NOW(), %s, %s)
        """
        values = (
            data['studentId'], data['studentName'], data['studentUSN'],
            data['type'], data['description'], data['priority'],
            data['currentHandler'], data['handlerRole']
        )
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'message': 'Grievance submitted successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/grievances/<grievance_id>', methods=['PUT'])
def update_grievance(grievance_id):
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            UPDATE grievances
            SET status = %s, last_updated = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (data['status'], grievance_id))
        conn.commit()
        return jsonify({'message': 'Grievance updated successfully'})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/grievances/<grievance_id>/forward', methods=['PUT'])
def forward_grievance(grievance_id):
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            UPDATE grievances
            SET current_handler = %s, handler_role = %s, status = 'forwarded', last_updated = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (data['to'], data['toRole'], grievance_id))
        conn.commit()
        return jsonify({'message': 'Grievance forwarded successfully'})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
