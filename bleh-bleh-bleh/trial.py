from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def send_webhook(webhook_url, message, file_path=None):
    data = {"content": message}
    files = None

    if file_path and os.path.exists(file_path):
        files = {"file": open(file_path, "rb")}

    response = requests.post(webhook_url, data=data, files=files)

    if files:
        files["file"].close()

    return response.status_code, response.text


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/send", methods=["POST"])
def send():
    webhook_url = request.form.get("webhook_url")
    message = request.form.get("message")
    attach_choice = request.form.get("attach_choice")
    file = request.files.get("file")

    file_path = None
    if attach_choice == "yes" and file and file.filename:
        file_path = os.path.join(BASE_DIR, file.filename)
        file.save(file_path)

    status, response = send_webhook(webhook_url, message, file_path)

    if status in [200, 204]:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": response}), 400


if __name__ == "__main__":
    app.run(debug=True)
