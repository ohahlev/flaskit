from flask import (
    send_file
)
from app import app


@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename)
