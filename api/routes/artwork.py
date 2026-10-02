from PIL import Image
from flask import Blueprint, request, current_app

from util.colors import get_global_color_tally, get_chunk_color_tally
from util.files import allowed_file, generate_filename
from util.images import convert_image_to_mc_colors, overlay_grid, convert_image_to_mc_colors_2

artwork = Blueprint('artwork', __name__)

@artwork.get("/<artwork_id>")
def get_artwork(artwork_id):
    if not artwork_id:
        return { "code": 400, "message": "Missing artwork id." }, 400

    if artwork_id not in current_app.CACHE:
        return { "code": 400, "message": "Artwork not found." }, 400

    _artwork = current_app.CACHE[artwork_id]

    return {
        "code": 200,
        "message": "Artwork found",
        "data": {
            "artwork_id": artwork_id,
            "target_rows": _artwork['rows'],
            "target_columns": _artwork['cols'],
            "color_counts": _artwork['color_counts'],
        }
    }, 200

@artwork.get("/<artwork_id>/counts/<row>/<col>")
def get_artwork_counts(artwork_id, row, col):
    if not artwork_id:
        return { "code": 400, "message": "Missing artwork id." }, 400

    if artwork_id not in current_app.CACHE:
        return { "code": 400, "message": "Artwork not found." }, 400

    _artwork = current_app.CACHE[artwork_id]

    chunk_count = get_chunk_color_tally(_artwork['num_grid'], int(row), int(col))

    return {
        "code": 200,
        "message": f"Color info for chunk {row}x{col}",
        "data": {
            "color_counts": chunk_count
        }
    }, 200

@artwork.post("convert")
def convert():

    if not request.files:
        return { "code": 400, "message": "Missing file to convert." }, 400

    file = request.files.get("file")

    if not file or file.filename == "":
        return { "code": 400, "message": "Missing file to convert." }, 400

    if not allowed_file(file.filename):
        return { "code": 400, "message": "Invalid file to convert."}, 400

    file_hash, file_ext = generate_filename(file)

    cols = int(request.form.get('target_columns', 1))
    rows = int(request.form.get('target_rows', 1))

    if file_hash in current_app.CACHE:
        if current_app.CACHE[file_hash]['rows'] == rows and current_app.CACHE[file_hash]['cols'] == cols:
            return {"code": 200, "message": "File already converted", "data": {"file_hash": file_hash}}, 200

    img = Image.open(file)

    converted_image, num_grid = convert_image_to_mc_colors_2(img, cols, rows)
    overlay_image = overlay_grid(converted_image, scale=10)
    color_counts = get_global_color_tally(num_grid)

    current_app.CACHE[file_hash] = {'image_preview': converted_image, 'num_grid': num_grid, 'color_counts': color_counts, 'overlay_image': overlay_image, 'ext': file_ext, 'rows': rows, 'cols': cols}

    return {"code": 200, "message": "File is now converting", "data": {"file_hash": file_hash, "ext": file_ext}}, 200