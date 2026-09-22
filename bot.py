import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured")

if not OWNER_CHAT_ID:
    raise RuntimeError("OWNER_CHAT_ID is not configured")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    photo = request.files.get("photo")

    if not photo:
        return jsonify({
            "success": False,
            "message": "No photo selected."
        }), 400

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if photo.mimetype not in allowed_types:
        return jsonify({
            "success": False,
            "message": "Only JPG, PNG and WebP images are allowed."
        }), 400

    # Maximum file size: 10 MB
    photo.seek(0, 2)
    file_size = photo.tell()
    photo.seek(0)

    if file_size > 10 * 1024 * 1024:
        return jsonify({
            "success": False,
            "message": "Image is too large. Maximum 10 MB."
        }), 400

    try:

        files = {
            "photo": (
                photo.filename,
                photo.stream,
                photo.mimetype
            )
        }

        data = {
            "chat_id": OWNER_CHAT_ID,
            "caption": "📸 Photo voluntarily submitted through Kurdiaii Bot."
        }

        response = requests.post(
            f"{TELEGRAM_API}/sendPhoto",
            data=data,
            files=files,
            timeout=30
        )

        if response.ok:
            return jsonify({
                "success": True,
                "message": "Photo sent successfully."
            })

        print("Telegram error:", response.text)

        return jsonify({
            "success": False,
            "message": "Telegram could not receive the photo."
        }), 500

    except Exception as error:

        print("Server error:", error)

        return jsonify({
            "success": False,
            "message": "Server error."
        }), 500


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
