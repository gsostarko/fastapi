from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection parameters
db_params = {
    'database': 'railway',
    'user': 'postgres',
    'password': 'eYl7DP0W10K3DMUH25md',
    'host': 'containers-us-west-98.railway.app',  # e.g., localhost or IP address
    'port': '6807'   # e.g., 5432
}

# Create a table to store data in PostgreSQL
def create_table():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id SERIAL PRIMARY KEY,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/upload', methods=['POST'])
def upload_data():
    try:
        data = request.json.get('data')  # Assuming JSON data
        if data is None:
            return jsonify({"message": "No data provided"}), 400

        # Save data to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO data (timestamp) VALUES (%s)", (data,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Data saved successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    create_table()  # Create the table if it doesn't exist
    app.run(host='containers-us-west-98.railway.app', port=6807)
