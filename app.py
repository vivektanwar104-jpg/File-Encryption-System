from flask import Flask, render_template, request, send_file
import os
from cryptography.fernet import Fernet
import base64
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/encrypt', methods=['POST'])
def encrypt():
    file = request.files['file']
    password = request.form['password']

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    with open(file_path, "rb") as f:
        data = f.read()

    key = generate_key(password)
    cipher = Fernet(key)

    encrypted_data = cipher.encrypt(data)

    encrypted_path = file_path + ".enc"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    return send_file(encrypted_path, as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    file = request.files['file']
    password = request.form['password']

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    with open(file_path, "rb") as f:
        data = f.read()

    key = generate_key(password)
    cipher = Fernet(key)

    try:
        decrypted_data = cipher.decrypt(data)
    except:
        return "❌ Wrong Password or Corrupted File!"

    if file_path.endswith(".enc"):
        decrypted_path = file_path[:-4]
    else:
        decrypted_path = file_path + "_decrypted"

    with open(decrypted_path, "wb") as f:
        f.write(decrypted_data)

    return send_file(decrypted_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)