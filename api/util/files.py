import hashlib
from typing import Tuple

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def generate_filename(file) -> Tuple[str, str]:
    filename = secure_filename(file.filename)
    new_filename = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    ext = secure_filename(file.filename).split(".")[-1]
    return new_filename, ext

def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS