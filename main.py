from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Configure the PostgreSQL database connection
db_conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="eYl7DP0W10K3DMUH25md",
    host="containers-us-west-98.railway.app",  # Change this if your database is on a different host
    port="6807"  # Change this if your PostgreSQL port is different
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if user_input:
            # Save the user input to the database
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO data (timestamp) VALUES (%s)", (user_input,))
            db_conn.commit()
            cursor.close()
            return redirect(url_for("index"))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
