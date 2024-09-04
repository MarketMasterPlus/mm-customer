# mm-customer/app.py

from app import create_app
from flask import jsonify

app = create_app()

# Optional: Health check endpoint to ensure the app is running
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # Running on 0.0.0.0 to allow external connections (e.g., from Docker)
    app.run(host='0.0.0.0', port=5701)
