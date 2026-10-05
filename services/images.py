import os, uuid
from PIL import Image
from werkzeug.utils import secure_filename

def save_upload(file, config):
    if not file or not file.filename:
        raise ValueError("Please choose an image.")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in config["ALLOWED_EXTENSIONS"]:
        raise ValueError("Only PNG, JPG, JPEG and WEBP images are allowed.")
    os.makedirs(config["UPLOAD_FOLDER"], exist_ok=True)
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(config["UPLOAD_FOLDER"], name)
    file.save(path)
    try:
        with Image.open(path) as image:
            image.verify()
    except Exception:
        os.remove(path)
        raise ValueError("The uploaded file is not a valid image.")
    return os.path.relpath(path, os.path.dirname(__file__) + "/..").replace("\\\\", "/")

def delete_file(path):
    if path and os.path.exists(path):
        os.remove(path)
